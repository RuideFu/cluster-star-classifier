# Notes!

## SVM

I opted to use the SVM classifier since it's a relatively simple problem that only has 2 classes(cluster and fields stars).

## Kernel

The most important hyperparameter is the kernel.
Knowing my data is not linearly separable and mostly Gaussian, I went with a Gaussian kernel. 
_[rbf in sklearn](https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.kernels.RBF.html)_.

## Data Preprocessing

I tried using outlier rejection to improve the model, but I don't think it's necessary since SVM is robust for that.

However, it's very helpful to frame the plots by removing 1% of the outliers.

## Standardization/Normalization

It doesn't seem that it's necessary to standardize the data. **TODO: further investigation needed.**



