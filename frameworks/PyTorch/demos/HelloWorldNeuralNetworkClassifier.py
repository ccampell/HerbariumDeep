"""
HelloWorldNeuralNetworkClassifier.py
Implementation of the Training a Classifier section of the PyTorch: A 60 Minute Blitz tutorial. Performs the following:
1. Loads and normalizes the CIFAR10 training and test datasets with torchvision
2. Defines a CNN
3. Defines a loss function
4. Trains the network on the training data
5. Evaluates the neural network via the loss function on the test data.
Source: http://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
"""

__author__ = "Chris Campell"
__version__ = "3/23/2018"

import torch
import torchvision
import torchvision.transforms as transforms

import matplotlib.pyplot as plt
import numpy as np

from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Input -> C1: feature maps 6 @ (28 x 28)
        # 3 input image channels, 6 output layers, 5x5 square convolution kernel
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)

        # Max pooling over a (2, 2) window
        self.pool = nn.MaxPool2d(kernel_size=(2, 2))

        # C1 -> C3: feature maps 16 @ (10 x 10)
        # 6 input channels, 16 output layers, 5x5 square convolution kernel
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5)

        # C3 -> S4: feature maps 16 @ (5 x 5) <last feature map layer>
        self.fc1 = nn.Linear(in_features=16 * 5 * 5, out_features=120)

        # S4 -> C5: Fully Connected Layer (120 x 1)
        self.fc2 = nn.Linear(in_features=120, out_features=84)

        # C5 -> F6: Fully Connected Layer (84 x 1)
        self.fc3 = nn.Linear(in_features=84, out_features=10)

    def forward(self, x):
        """
        forward: Performs a forward pass through the network. Architecturally, this method defines the connections
            between layers in the network (how to get the output of the neural net). This function is called when
            applying the neural net to an input autograd.Variable:
                net = Net()
                net(input) # calls net.forward(input)
        :param x: The input to the neural network.
        :return x: The input to the neural network after undergoing a forward pass through the net.
        """
        '''
        F is a module housing functions (such as pooling) as well as various activation functions. 
        '''
        # Max pooling over a (2, 2) window during the forward pass:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        '''
        The view function takes a Tensor and re-shapes it. Here we are resizing x to a matrix of size:
            (-1 x self.num_flat_features(x)). Of course the -1 isn't really negative one; it means to auto-infer the 
            dimensionality from the other dimensions (see: http://pytorch.org/docs/master/tensors.html#torch.Tensor.view)
        In this particular case the inferred dimension is 1, as we are changing x to a vector with 
            (1 x self.num_flat_features(x))
        '''
        x = x.view(-1, (16 * 5 * 5))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # Here we pass through the output layer and return the result:
        x = self.fc3(x)
        return x

'''
We can view some of the training images:
'''
def imshow(img):
    img = img / 2 + 0.5         # un-normalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


def test_classifier(net, testloader, classes):
    """
    test_classifier: Tests the neural network by first displaying testing images with correct label, and then the network's
        prediction. Afterward the network is tested on the entire dataset.
    :param net: A nn.Module instance representing the neural network.
    :param testloader: A nn.data.DataLoader instance which performs loading.
    :return:
    """
    dataiter = iter(testloader)
    images, labels = dataiter.next()

    # Print the true labels in the test set for four classes:
    print('GroundTruth: ', ' '.join('%5s' % classes[labels[j]] for j in range(4)))
    # predict:
    outputs = net(Variable(images))
    # predict class labels:
    _, predicted = torch.max(outputs.data, 1)
    print('Predicted: ', ' '.join('%5s' % classes[predicted[j]] for j in range(4)))
    # print images
    plt.clf()
    imshow(torchvision.utils.make_grid(images))
    plt.show()

    # evaluate the network:
    correct = 0
    total = 0
    for data in testloader:
        images, labels = data
        outputs = net(Variable(images))
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum()
    print('Accuracy of the network on the 10,000 test images: %d %%' % (100 * correct / total))

    # Lets look at the classes that did well compared to those that did poorly:
    class_correct = list(0. for i in range(10))
    class_total = list(0. for i in range(10))
    for data in testloader:
        images, labels = data
        outputs = net(Variable(images))
        _, predicted = torch.max(outputs.data, 1)
        c = (predicted == labels).squeeze()
        for i in range(4):
            label = labels[i]
            class_correct[label] += c[i]
            class_total[label] += 1

    for i in range(10):
        print('Accuracy of %5s: %2d %%' % (classes[i], 100 * class_correct[i] / class_total[i]))


def train(net, trainloader):
    """
    train: Trains a PyTorch neural network (nn.Module) via optimizer.
    :param net: A nn.Module instance representing the neural network.
    :param trainloader: A nn.data.DataLoader instance which performs loading.
    :return:
    """
    # Use Cross Entropy as a loss function:
    criterion = nn.CrossEntropyLoss()
    # Use Stochastic Gradient Descent (SGD) with momentum for an update rule:
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    # We only need two epochs apparently:
    num_epochs = 2
    # Iterate over the dataset num_epochs times:
    for epoch in range(num_epochs):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # get the inputs:
            inputs, labels = data
            # wrap them in an autograd.Variable:
            inputs, labels = Variable(inputs), Variable(labels)
            # zero the parameter gradients:
            optimizer.zero_grad()
            # compute the forward pass:
            outputs = net(inputs)
            # compute the loss:
            loss = criterion(outputs, labels)
            # perform backpropagation:
            loss.backward()
            # update the weights with the update/learning rule:
            optimizer.step()

            # print statistics:
            running_loss += loss.data[0]
            if i % 2000 == 1999:        # print every 2000 mini-batches
                print('<epoch, batch>:\t\t[%d, %5d] loss: %.3f' % (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0
    print('Finished Training')

def main():
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=4, shuffle=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(testset, batch_size=4, shuffle=False, num_workers=2)

    classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

    # grab some random training images:
    dataiter = iter(trainloader)
    images, labels = dataiter.next()

    # print labels
    print(' '.join('%5s' % classes[labels[j]] for j in range(4)))

    # show images
    imshow(torchvision.utils.make_grid(images))

    # instantiate the network:
    net = Net()

    # train the network:
    train(net, trainloader)

    # test the network:
    test_classifier(net, testloader, classes)


'''
The torchvision package contains the CIFAR10 dataset. This dataset has the classes: 
    ‘airplane’, ‘automobile’, ‘bird’, ‘cat’, ‘deer’, ‘dog’, ‘frog’, ‘horse’, ‘ship’, ‘truck’. 
The images in CIFAR-10 are of size 3x32x32, i.e. 3-channel color images of 32x32 pixels in size. 
'''
if __name__ == '__main__':
    # The output of torchvision datasets are PILImage images of range [0, 1]. We transform them to
    #   Tensors of normalized range [-1, 1].
    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))])

    '''
    NOTE: This script was executed on a windows 10 x86_64 machine, which required moving torch.utils.data.DataLoader's
        to the main method. This script will not run without 'if __name__ == '__main__' on a windows machine. It will
        not run if you issue calls to torch.utils.data.DataLoader() from the global scope (i.e. in this method). 
    '''

    # Download (or load if already present) the CIFAR10 training dataset:
    trainset = torchvision.datasets.CIFAR10(root='/data', train=True, download=True, transform=transform)

    # Download (or load if already present) the CIFAR10 test dataset:
    testset = torchvision.datasets.CIFAR10(root='/data', train=False, download=True, transform=transform)

    main()
