import matplotlib.pyplot as plt
import numpy as np

# x = np.array([1,2,3,4])
# y = np.array([4,3,2,1])

# plt.plot(x,y,'r-',linewidth=3)
# plt.show()

mu, sigma =0, 15
x = mu + sigma * np.random.randn(10000)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title('Histogram of IQ')
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show()