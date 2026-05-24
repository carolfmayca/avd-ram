#!/usr/bin/env python3
"""
M/M/1 Queue Simulation
λ = 9 clients/s,  μ = 10 clients/s

Usage
-----
    python mm1.py -e 1              # fixed-n runs (n = 10³, 10⁵, 10⁷, 10⁹)
    python mm1.py -e 2              # Chow-Robbins stopping rule
    python mm1.py -e 3              # relative-CI stopping rule
    python mm1.py -e 1 --seed 42    # reproducible run
    python mm1.py -e 1 --max-n 7    # skip n=10⁹ (cap exponent at 7)
"""

import argparse
import textwrap
import time

import numpy as np

# ── Queue parameters ──────────────────────────────────────────────────────────
LAM = 9.0  # arrival rate  λ  (clients / second)
MU = 10.0  # service rate  μ  (clients / second)
Z95 = 1.96  # z_{0.975}  for 95% CI
BATCH_SIZE = 1_000_000  # customers generated per internal batch


# ── Theoretical reference ────────────────────────────────────────────────────
def theoretical_mean(lam: float = LAM, mu: float = MU) -> float:
    """
    Waiting-time mean from Queueing Theory:
        E[X] = ρ · (1/μ) / (1 − ρ),   ρ = λ/μ
    """
    rho = lam / mu
    return rho / (mu * (1.0 - rho))


# ── Online statistics (parallel Welford) ─────────────────────────────────────
class OnlineStats:
    """
    Accumulates sample count, mean, and variance incrementally
    without storing individual observations.

    Uses the parallel (batch) form of Welford's algorithm so that
    an entire numpy batch can be merged in O(1) extra passes.
    """

    __slots__ = ("n", "_mean", "_M2")

    def __init__(self) -> None:
        self.n = 0
        self._mean = 0.0
        self._M2 = 0.0  # sum of squared deviations from running mean

    def add_batch(self, xs: np.ndarray) -> None:
        """Merge a batch of observations into the running statistics."""
        n_b = len(xs)
        mean_b = float(xs.mean())
        M2_b = float(((xs - mean_b) ** 2).sum())

        if self.n == 0:
            self.n, self._mean, self._M2 = n_b, mean_b, M2_b
        else:
            n_new = self.n + n_b
            delta = mean_b - self._mean
            self._mean += delta * n_b / n_new
            self._M2 += M2_b + delta**2 * self.n * n_b / n_new
            self.n = n_new

    # ── derived quantities ────────────────────────────────────────────────────
    @property
    def mean(self) -> float:
        return self._mean

    @property
    def variance(self) -> float:
        return self._M2 / (self.n - 1) if self.n > 1 else float("inf")

    def half_width(self) -> float:
        """H = z_{0.975} · s / √n  (half-width of 95% CI)."""
        if self.n < 2:
            return float("inf")
        return Z95 * (self.variance / self.n) ** 0.5

    def ci(self) -> tuple[float, float]:
        H = self.half_width()
        return self._mean - H, self._mean + H


# ── Core simulation kernel ────────────────────────────────────────────────────
def _lindley_loop(
    ia: list[float],
    st: list[float],
    se: float,
    t: float,
) -> tuple[list[float], float, float]:
    """
    Apply Lindley's recursion to one batch of customers.

        W[i]   = max(0,  prev_service_end − arrival_i)
        se_new = arrival_i + W[i] + service_i

    Parameters
    ----------
    ia  : inter-arrival times (Python list, faster element access than ndarray)
    st  : service times       (Python list)
    se  : server-busy-until time carried over from the previous batch
    t   : last arrival time   carried over from the previous batch

    Returns
    -------
    (waiting_times, new_se, new_t)
    """
    n = len(ia)
    waiting = [0.0] * n
    for i in range(n):
        t += ia[i]
        ss = t if t > se else se  # service_start = max(arrival, se)
        waiting[i] = ss - t  # W_i = service_start − arrival_i ≥ 0
        se = ss + st[i]
    return waiting, se, t


# ── High-level simulator ──────────────────────────────────────────────────────
class MM1Queue:
    """
    M/M/1 queue simulator.

    Random numbers are drawn from numpy in bulk (fast); the sequential
    Lindley recursion is evaluated in a tight Python loop over Python lists
    (faster per-element access than numpy arrays in a loop).
    Online statistics are maintained with the parallel Welford algorithm.
    """

    def __init__(self, lam: float = LAM, mu: float = MU, seed=None) -> None:
        self.lam = lam
        self.mu = mu
        self.rng = np.random.default_rng(seed)
        self._reset()

    # ── internal helpers ──────────────────────────────────────────────────────
    def _reset(self) -> None:
        self._se = 0.0  # server busy-until time
        self._t = 0.0  # time of last arrival
        self.stats = OnlineStats()

    def _step(self, size: int) -> None:
        """Generate `size` customers, simulate, update online stats."""
        # Generate in numpy (vectorised), then convert to list for fast loop
        ia = self.rng.exponential(1.0 / self.lam, size).tolist()
        st = self.rng.exponential(1.0 / self.mu, size).tolist()

        waiting, self._se, self._t = _lindley_loop(ia, st, self._se, self._t)

        self.stats.add_batch(np.array(waiting, dtype=np.float64))

    # ── Exercise 1 ────────────────────────────────────────────────────────────
    def run_fixed(self, n: int) -> tuple[float, float]:
        """
        Simulate exactly n customers.

        Returns
        -------
        (mean, H)  where the 95% CI is  [mean − H,  mean + H]
        """
        self._reset()
        done = 0
        while done < n:
            self._step(min(BATCH_SIZE, n - done))
            done = self.stats.n
        return self.stats.mean, self.stats.half_width()

    # ── Exercise 2 ────────────────────────────────────────────────────────────
    def run_chow_robbins(
        self, d: float, min_n: int = 1_000
    ) -> tuple[int, float, float]:
        """
        Chow-Robbins stopping rule: stop when H ≤ d  (CI width ≤ 2d)
        and n ≥ min_n.

        Returns
        -------
        (n, mean, H)
        """
        self._reset()
        while True:
            self._step(BATCH_SIZE)
            if self.stats.n >= min_n and self.stats.half_width() <= d:
                break
        return self.stats.n, self.stats.mean, self.stats.half_width()

    # ── Exercise 3 ────────────────────────────────────────────────────────────
    def run_relative_ci(
        self, gamma: float = 0.05, min_n: int = 1_000
    ) -> tuple[int, float, float]:
        """
        Relative-CI stopping rule: stop when H / X̄ ≤ γ  and n ≥ min_n.

        Returns
        -------
        (n, mean, H)
        """
        self._reset()
        while True:
            self._step(BATCH_SIZE)
            s = self.stats
            if s.n >= min_n and s.mean > 0 and s.half_width() / s.mean <= gamma:
                break
        return self.stats.n, self.stats.mean, self.stats.half_width()


# ── Pretty-print helpers ──────────────────────────────────────────────────────
def _banner(title: str) -> None:
    bar = "=" * 72
    print(f"\n{bar}")
    print(f"  {title}")
    rho = LAM / MU
    E = theoretical_mean()
    print(f"  λ = {LAM}  |  μ = {MU}  |  ρ = {rho}  |  E[X] = {E:.6f} s")
    print(bar)


# ── Exercise runners ──────────────────────────────────────────────────────────
def exercise1(sim: MM1Queue, max_exp: int = 9) -> None:
    """Fixed-n simulation for n ∈ {10³, 10⁵, 10⁷, 10⁹}."""
    _banner("Exercise 1 — Fixed-n simulation")
    E = theoretical_mean()
    ns = [10**k for k in [3, 5, 7, 9] if k <= max_exp]

    W = 13
    hdr = (
        f"\n{'n':>{W}} | {'X̄(n)':>{W}} | {'CI lower':>{W}} | "
        f"{'CI upper':>{W}} | {'H':>{W}} | {'|X̄ − E[X]|':>{W}} | {'wall-time':>10}"
    )
    sep = "─" * len(hdr)
    print(hdr)
    print(sep)

    for n in ns:
        t0 = time.perf_counter()
        mean, H = sim.run_fixed(n)
        elapsed = time.perf_counter() - t0
        lo, hi = mean - H, mean + H
        err = abs(mean - E)
        print(
            f"{n:{W},} | {mean:{W}.6f} | {lo:{W}.6f} | "
            f"{hi:{W}.6f} | {H:{W}.6f} | {err:{W}.6f} | {elapsed:>9.5f}s"
        )

    print()


def exercise2(sim: MM1Queue) -> None:
    """Chow-Robbins stopping rule for d ∈ {1.0, 0.5, 0.1, 0.05}."""
    _banner("Exercise 2 — Chow-Robbins stopping rule  (stop when H ≤ d)")
    ds = [1.0, 0.5, 0.1, 0.05]
    W = 14

    hdr = (
        f"\n{'d':>8} | {'n (final)':>{W}} | {'X̄(n)':>12} | "
        f"{'H':>12} | {'2d':>8} | {'H ≤ d?':>8} | {'wall-time':>10}"
    )
    sep = "─" * len(hdr)
    print(hdr)
    print(sep)

    for d in ds:
        t0 = time.perf_counter()
        n, mean, H = sim.run_chow_robbins(d)
        elapsed = time.perf_counter() - t0
        ok = "✓" if H <= d else "✗"
        print(
            f"{d:>8.2f} | {n:{W},} | {mean:>12.6f} | "
            f"{H:>12.6f} | {2*d:>8.4f} | {ok:>8} | {elapsed:>9.5f}s"
        )

    print()


def exercise3(sim: MM1Queue) -> None:
    """Relative-CI stopping rule with γ = 5 %."""
    _banner("Exercise 3 — Relative-CI stopping rule  (stop when H / X̄ ≤ γ = 5%)")
    E = theoretical_mean()

    t0 = time.perf_counter()
    n, mean, H = sim.run_relative_ci(gamma=0.05)
    elapsed = time.perf_counter() - t0

    lo, hi = mean - H, mean + H
    print()
    print(f"  n (final)  = {n:,}")
    print(f"  X̄(n)      = {mean:.6f} s")
    print(f"  H          = {H:.6f} s")
    print(f"  H / X̄     = {H / mean:.4%}   (target ≤ 5 %)")
    print(f"  95 % CI    = [ {lo:.6f} ,  {hi:.6f} ]")
    print(f"  E[X]       = {E:.6f} s   (theoretical)")
    print(f"  wall-time  = {elapsed:.5f} s")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mm1.py",
        description="M/M/1 queue simulation  (λ=9 clients/s, μ=10 clients/s)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Exercises
            ---------
              1  Fixed-n simulation    n ∈ {10³, 10⁵, 10⁷, 10⁹}
                   Compare X̄(n) and 95 % CI against theoretical E[X].
              2  Chow-Robbins rule     d ∈ {1.0, 0.5, 0.1, 0.05}
                   Stop when CI half-width H ≤ d; report final n.
              3  Relative-CI rule      γ = 5 %
                   Stop when H / X̄ ≤ γ; report X̄(n), H, and n.

            Notes
            -----
              • n = 10⁹ in exercise 1 may take several minutes on a laptop.
                Use --max-n 7 to cap at n = 10⁷.
              • --seed fixes numpy's RNG for reproducible results.
        """
        ),
    )
    parser.add_argument(
        "-e",
        "--exercise",
        type=int,
        choices=[1, 2, 3],
        required=True,
        metavar="{1,2,3}",
        help="Exercise to run (1, 2, or 3).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Integer seed for the random-number generator.",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=9,
        metavar="EXP",
        help=(
            "(Exercise 1 only) Maximum exponent: largest n = 10^EXP. "
            "Default: 9  (i.e. n = 10⁹).  Use 7 to stop at 10⁷."
        ),
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    sim = MM1Queue(seed=args.seed)

    dispatch = {
        1: lambda: exercise1(sim, max_exp=args.max_n),
        2: lambda: exercise2(sim),
        3: lambda: exercise3(sim),
    }
    dispatch[args.exercise]()


if __name__ == "__main__":
    main()
