# Method 1: Wavelength Shift Estimation from Sun Spectrum

This method calculates the wavelength shift between a measured solar spectrum and a synthetic reference spectrum.

The reference spectrum and its wavelength grid are loaded from the **synthetic spectrum section of the Pandora calibration file**. The measured spectrum is read from the Pandora L0 file and dark-corrected before fitting.

For each trial wavelength shift, the reference wavelength grid is shifted and the reference spectrum is interpolated onto the measured wavelength grid. A linear least-squares fit is then performed:

\[
M(\lambda) \approx aR(\lambda-\Delta\lambda)+b
\]

where \(M\) is the measured spectrum, \(R\) is the reference spectrum, \(a\) is a scale factor, \(b\) is an offset, and \(\Delta\lambda\) is the wavelength shift.

The shift with the minimum mean squared error is selected, followed by a three-point parabolic refinement for sub-step accuracy.

## Outputs

- Best grid-based wavelength shift
- Refined wavelength shift
- Measured wavelength correction
- RMSE and MSE
- Scale factor and offset
- Aligned reference spectrum
- Residual spectrum

## Example Results

Add figures showing:

- Measured and synthetic spectra before alignment
- Measured and aligned spectra after correction
- Mean squared error versus trial wavelength shift
- Wavelength shift versus measurement time
