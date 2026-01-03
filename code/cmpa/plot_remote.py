from __future__ import annotations

import matplotlib.pyplot as plt

from .remote import RemoteResult


def plot_remote(result: RemoteResult, *, show_tilde: bool = True) -> None:
    # Wykres rho
    plt.figure()
    plt.plot(result.mjd, result.rho)
    plt.xlabel("MJD")
    plt.ylabel(f"rho(goal/start), rho0_prod={result.rho0_prod:g}")
    plt.title("Remote frequency ratio")
    plt.tight_layout()
    plt.show()

    if show_tilde:
        plt.figure()
        plt.plot(result.mjd, result.tilde_rho)
        plt.xlabel("MJD")
        plt.ylabel("tilde_rho = rho/rho0_prod - 1")
        plt.title("Remote reduced ratio")
        plt.tight_layout()
        plt.show()
