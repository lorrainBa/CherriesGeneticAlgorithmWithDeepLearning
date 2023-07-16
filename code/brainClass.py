import numpy as np

class Brain():
    #Number of neuron on first layer
    n1 = 3
    #Numer of neuron on last layer to get the x and y coord
    n2 = 2
    #Numer of neuron on last layer to get the output (coef,xspeed,ypseed)
    n3 = 3

    def __init__(self,numberOfBrainCaptor, brainParameters = False):
        #Get the number of parameters
        n0 = numberOfBrainCaptor
        #Number of neuron on first layer
        n1 = self.n1
        #Numer of neuron on last layer to get the x and y coord
        n2 = self.n3
        #Number of parameters on the second layer
        n3 = self.n1
        self.brainParameters = {}

        if brainParameters == False:
            W1 = np.random.randn(n1,n0)
            b1 = np.random.randn(n1,1)

            W2 = np.random.randn(n3,n1)
            b2 = np.random.randn(n3,1)

            W3 = np.random.randn(n2,n3)
            b3 = np.random.randn(n2,1)

            
            #Important variables
            self.brainParameters = {
                'W1' : W1,
                'b1' : b1,
                'W2' : W2,
                'b2' : b2,
                'W3' : W3,
                'b3' : b3
            }

        else:
            self.brainParameters = brainParameters

    def prediction(self,X):

        
        """print("parametres",self.brainParameters)"""
        W1 = self.brainParameters['W1']
        b1 = self.brainParameters['b1']
        W2 = self.brainParameters['W2']
        b2 = self.brainParameters['b2']
        W3 = self.brainParameters['W3']
        b3 = self.brainParameters['b3']
        
        
        Z1 = W1.dot(X) + b1
        


        #relu activation
        """A1 = 1 / (1+np.exp(-Z1))"""
        """print(" A1", A1)"""

        Z2 = W2.dot(Z1) + b2
        

        """A2 = 1 / (1+np.exp(-Z2))"""
        """print(" A2", A2)"""

        Z3 = W3.dot(Z2) + b3
        
        A3=Z3
        #Softmax activation
        """A3 = np.tanh(Z3)"""
        
        """A20 = A3[0][0] /2
        A21 = A3[1][0] /2"""
        temp = abs(A3[0][0])
        if temp >1:
            A20 = 1
        else:
            A20 = abs(A3[0][0])
        
        A21 = A3[1][0] / (abs(A3[1][0])+abs(A3[2][0]))
        A22 = A3[2][0] / (abs(A3[1][0])+abs(A3[2][0]))
        A3[0][0] = A20
        A3[1][0]= A21
        A3[2][0]= A22
        
        """print("entrée", X)
        print("w1 dot",W1.dot(X))
        print("b1", b1)
        print(" som", Z1)
        print(" Z2", Z2)
        print(" Z3", Z3)
        print("sortieNormalised", A3)"""
        
        return(A3)

    def updateNeuralNetworks(self,parameters,mutation):
        W1 = self.brainParameters['W1']
        b1 = self.brainParameters['b1']
        W2 = self.brainParameters['W2']
        b2 = self.brainParameters['b2']

        W1 = W1 + mutation
        b1 = b1 + mutation
        W2 = W2 + mutation
        b2 = b2 + mutation

        self.brainParameters = {
            'W1' : W1,
            'b1' : b1,
            'W2' : W2,
            'b2' : b2
        }


    def softmax(self,X):


        return(np.exp(X)/np.exp(X).sum())

    def getBrainParameters(self):
        return(self.brainParameters)