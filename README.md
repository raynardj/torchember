# Torch Ember
> Tracking and visualize after the burning pytorch


## Installation
```pip install torchember```

## Fast Tutorial

Full [documentations](https://raynardj.github.io/torchember/)

### Step1, Track your model

Place you torch ember tracker on your model

```python
from torchember.core import torchEmber
te = torchEmber(model)
```

Train your model as usual

### Step2, Check the analysis on the WebUI

Run the service from terminal
```shell
$ torchember
```
The default port will be 8080

Or assign a port
```shell
$ torchember --port=4200
```

Visit your analysis at ```http://[host]:[port]```
