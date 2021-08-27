
import torch
from torch import nn, add, cat



class SRS3(nn.Module):

    def __init__(self, NUM_CHANNELS=1, n_filters1=64, n_filters2=32):
        super(SRS3, self).__init__()

        self.n_filters1 = n_filters1
        self.n_filters2 = n_filters2
        
        self.conv11 = nn.Conv2d(NUM_CHANNELS, self.n_filters1, kernel_size=5, padding=2)
        self.conv21 = nn.Conv2d(self.n_filters1, self.n_filters1, kernel_size=9, padding=4)
        self.conv31 = nn.Conv2d(self.n_filters1, self.n_filters1, kernel_size=13, padding=6)
        self.ca = ChannelAttention(input_planes=self.n_filters1*3, latent_planes=self.n_filters1)
        self.conv2 = nn.Conv2d(self.n_filters1*3, self.n_filters2, kernel_size=1, padding=0)
        self.conv3 = nn.Conv2d(self.n_filters2, NUM_CHANNELS, kernel_size=5, padding=2)
        self.lrelu11 = nn.LeakyReLU(inplace=True)
        self.lrelu21 = nn.LeakyReLU(inplace=True)
        self.lrelu31 = nn.LeakyReLU(inplace=True)        
        self.lrelu2 = nn.LeakyReLU(inplace=True)


    def forward(self, x):

        residual = x
        x1 = self.lrelu11(self.conv11(x))
        x2 = self.lrelu21(self.conv21(x1))
        x3 = self.lrelu31(self.conv31(x2))
        x = cat((x1,x2,x3),1)
        x = self.ca(x) * x + x
        x = self.lrelu2(self.conv2(x))
        x = self.conv3(x)
        out = x
        return out
        


class ChannelAttention(nn.Module):
    def __init__(self, input_planes=64, latent_planes=32):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc1   = nn.Conv2d(input_planes, latent_planes, 1, bias=False)        
        self.relu1 = nn.LeakyReLU()
        self.fc2   = nn.Conv2d(latent_planes, input_planes, 1, bias=False)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        avg_out = self.fc2(self.relu1(self.fc1(self.avg_pool(x))))
        out = avg_out
        return self.softmax(out)

