import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

def impulse_invariant_method(b_analog, a_analog, fs):
    """
    Converts an analog filter (b, a) to a digital filter using the 
    Impulse Invariance Method.
    
    H(z) = Sum ( r_k / (1 - exp(p_k * T) * z^-1) )
    """
    # 1. Partial fraction expansion of Analog Transfer Function
    r, p, k = signal.residue(b_analog, a_analog)
    
    # 2. Map poles to Z-domain: p_z = exp(p_s * T)
    T = 1.0 / fs
    p_digital = np.exp(p * T)
    
    # 3. Map residues (residues remain same for h[n] = h(nT) assumption usually, 
    #    sometimes scaled by T to normalize gain. We'll use strict sampling).
    #    Strict Impulse Invariance: h[n] = T * h_a(nT) implies multiplying residues by T?
    #    Actually standard Textbooks (Oppenheim/Schafer) often say h[n] = h_a(nT).
    #    Let's stick to unscaled residues -> h[n] = h_a(nT). 
    #    Gain might need normalization if desired, but for raw method, this is it.
    r_digital = r * T  # Often included to keep gain consistent with Bilinear-like magnitude
    
    # 4. Convert back to numerator/denominator in Z-domain
    #    Start with k (direct term). If causal strictly proper, k=0.
    
    # Constructing H(z) from sum of first order terms:
    # H(z) = sum( r_i / (1 - p_i z^-1) )
    # We combine these terms into a single rational function.
    
    # We can use invresz to go back, but scipy's invresz assumes z terms.
    # Let's use signal.invresz which creates b(z)/a(z) from r, p, k
    # But invresz expects p to be poles, and format is H(z) = R(z)/P(z).
    b_dig, a_dig = signal.invresz(r_digital, p_digital, k)
    
    return b_dig, a_dig

def analyze_filter(b, a, fs, title):
    # Frequency Response
    w, h = signal.freqz(b, a, worN=4096, fs=fs)
    
    plt.figure(figsize=(10, 8))
    
    # Magnitude
    plt.subplot(3, 1, 1)
    plt.plot(w, 20 * np.log10(np.abs(h) + 1e-12))
    plt.title(f"{title} - Magnitude Response")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.grid(True)
    
    # Phase
    plt.subplot(3, 1, 2)
    plt.plot(w, np.unwrap(np.angle(h)))
    plt.title(f"{title} - Phase Response")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (radians)")
    plt.grid(True)
    
    # Impulse Response
    # Create an impulse
    impulse_len = 100
    imp = np.zeros(impulse_len)
    imp[0] = 1.0 / fs # Unit impulse in continuous sense approximation? No, digital unit sample.
    imp[0] = 1.0 
    
    h_imp = signal.lfilter(b, a, imp)
    t_imp = np.arange(impulse_len) / fs
    
    plt.subplot(3, 1, 3)
    plt.stem(t_imp * 1000, h_imp) # Plot vs ms
    plt.title(f"{title} - Impulse Response")
    plt.xlabel("Time (ms)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{title.replace(' ', '_')}.png")
    # plt.show() # Commented out to run in background, can uncomment if interactive
    print(f"Filter: {title}")
    
    # Stability Check
    poles = np.roots(a)
    print("  Simply Poles:", poles)
    max_pole = np.max(np.abs(poles))
    print(f"  Max Pole Magnitude: {max_pole:.4f}")
    if max_pole < 1.0:
        print("  Stability: STABLE (All poles inside unit circle)")
    else:
        print("  Stability: UNSTABLE")
    print("-" * 30)

def main():
    fs = 20000
    
    print("Digital Filter Design Project")
    print(f"Sampling Frequency: {fs} Hz")
    print("-" * 30)
    
    # ==========================
    # Task 1: BPF (2 kHz - 4 kHz)
    # ==========================
    # Analog Prototype: Butterworth Bandpass
    # N=2 (Second order prototype) -> Bandpass becomes 2*N = 4th order
    # Critical Frequencies: 2000, 4000 Hz -> Angular: 2*pi*f
    f1 = 2000
    f2 = 4000
    ws = [2 * np.pi * f1, 2 * np.pi * f2]
    
    # Design Analog Filter
    b_analog_bpf, a_analog_bpf = signal.butter(N=2, Wn=ws, btype='bandpass', analog=True)
    
    # Discretize
    b_bpf, a_bpf = impulse_invariant_method(b_analog_bpf, a_analog_bpf, fs)
    
    analyze_filter(b_bpf, a_bpf, fs, "Task 1_ BPF 2-4kHz")
    
    # ==========================
    # Task 2: LPF or HPF (3 kHz) -> Choosing LPF
    # ==========================
    # Analog Prototype: Butterworth Lowpass
    # N=2
    fc = 3000
    wc = 2 * np.pi * fc
    
    # Design Analog Filter
    b_analog_lpf, a_analog_lpf = signal.butter(N=2, Wn=wc, btype='lowpass', analog=True)
    
    # Discretize
    b_lpf, a_lpf = impulse_invariant_method(b_analog_lpf, a_analog_lpf, fs)
    
    analyze_filter(b_lpf, a_lpf, fs, "Task 2_ LPF 3kHz")

if __name__ == "__main__":
    main()
