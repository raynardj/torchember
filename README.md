# Torch Ember
> Tracking and visualize after the burning pytorch


## Tutorial & Docs
* Instant colab tutorial here: <a href="https://colab.research.google.com/github/raynardj/torchember/blob/master/nb_test/torchember_instant_tutorial.ipynb" target="_parent"><img src="https://camo.githubusercontent.com/52feade06f2fecbf006889a904d221e6a730c194/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667" alt="Open In Colab" data-canonical-src="https://colab.research.google.com/assets/colab-badge.svg"></a>

* Full [documentations](https://raynardj.github.io/torchember/)

## Installation
```pip install torchember```

## This framework tracks the pytorch model:

* On ```nn.Module``` level
* Down to the metrics/ features of all tensors, includes
    * inputs/outputs of each module
    * weight/grad tensors
* By **minimal** extra coding

![WebUI](nbs/001.png)

## Other lovely features
* Customizable metrics, with easy decorator syntax
* Split the tracking log in the way you like, just ```mark(k=v,k1=v2...)```
* You can easily switch on/off the tracking:
    * Even cost of computation is tiny, torchember don't have to calculate metric for every iteration
    * Hence, you can track eg. only the last steps, only each 200 steps .etc

### Step1, Track your model

Place you torch ember tracker on your model

```python
from torchember.core import torchEmber
te = torchEmber(model)
```

The above can track input and output of every module,The following can track status of every module

```python
for i in range(1000):
    ...
    loss.backward()
    optimizer.step()
    
    te.log_model()

```

Train your model as usual

### Step2, Check the analysis on the WebUI

WebUI intro video

<iframe width="560" height="315" src="https://www.youtube.com/embed/2NbXDqcZKPY" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

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

