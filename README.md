# Method 1: Wavelength Shift Estimation from Sun Spectrum

This method calculates the wavelength shift between a measured solar spectrum and a synthetic reference spectrum.

The reference spectrum and its wavelength grid are loaded from the **synthetic spectrum section of the Pandora calibration file**. The measured spectrum is read from the Pandora L0 file and dark-corrected before fitting.

## Least-Squares Spectral Fitting

For each trial wavelength shift, the shifted reference spectrum is fitted to the measured spectrum using

$$
M(\lambda) \approx aR(\lambda-\Delta\lambda)+b
$$

where

- $M(\lambda)$ = measured spectrum
- $R(\lambda-\Delta\lambda)$ = shifted reference spectrum
- $a$ = scale factor
- $b$ = constant offset
- $\Delta\lambda$ = wavelength shift

The scale factor compensates for differences in signal intensity, while the constant offset accounts for baseline differences between the measured and reference spectra.

## Fitting Error

The residual spectrum is calculated as

$$
r_i = M_i - \left(aR_i + b\right)
$$

The mean squared error (MSE) is then computed as

$$
\mathrm{MSE}=\frac{1}{N}\sum_{i=1}^{N}r_i^2
$$

where $N$ is the number of wavelength samples used in the fit.

The MSE is calculated for every trial wavelength shift, and the shift corresponding to the minimum MSE is selected as the best wavelength alignment.
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


# Method 2: Wavelength Shift Estimation using Hg Lamp

This method calculates the wavelength shift between a measured Hg lamp spectrum and a reference Hg spectrum.

Hg lamp measurement is done during Pandora calibration and can be found in Lab calibration L0 file. This Hg spectrum is read from the Lab calibration L0 file, dark-corrected before fitting and considered as reference spectrum.
