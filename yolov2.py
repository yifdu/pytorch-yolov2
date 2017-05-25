'''YOLOv2/Darknet in PyTorch.'''
import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F

from torch.autograd import Variable


class YOLOv2(nn.Module):
    cfg1 = [32, 'M', 64, 'M', 128, 64, 128, 'M', 256, 128, 256, 'M', 512, 256, 512, 256, 512]  # conv1 - conv13
    cfg2 = ['M', 1024, 512, 1024, 512, 1024]  # conv14 - conv18

    def __init__(self):
        super(YOLOv2, self).__init__()
        self.layer1 = self._make_layers(self.cfg1, in_planes=3)
        self.layer2 = self._make_layers(self.cfg2, in_planes=512)

        #### Add new layers
        self.conv19 = nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1)
        self.bn19 = nn.BatchNorm2d(1024)
        self.conv20 = nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1)
        self.bn20 = nn.BatchNorm2d(1024)
        # Currently I removed the passthrough layer for simplicity
        self.conv21 = nn.Conv2d(1024, 1024, kernel_size=3, stride=1, padding=1)
        self.bn21 = nn.BatchNorm2d(1024)
        # Outputs: 5boxes * (4coordinates + 1confidence + 20classes)
        self.conv22 = nn.Conv2d(1024, 5*(5+20), kernel_size=1, stride=1, padding=0)

    def _make_layers(self, cfg, in_planes):
        layers = []
        for x in cfg:
            if x == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True)]
            else:
                layers += [nn.Conv2d(in_planes, x, kernel_size=3, padding=1),
                           nn.BatchNorm2d(x),
                           nn.ReLU(True)]
                in_planes = x
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = F.relu(self.bn19(self.conv19(out)))
        out = F.relu(self.bn20(self.conv20(out)))
        out = F.relu(self.bn21(self.conv21(out)))
        out = self.conv22(out)
        return out


def test():
    net = YOLOv2()
    y = net(Variable(torch.randn(1,3,416,416)))
    print(y.size())  # [1,125,13,13]

# test()