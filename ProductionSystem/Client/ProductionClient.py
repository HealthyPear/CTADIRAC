""" Class that contains client access to the transformation DB handler. """

__RCSID__ = "$Id$"

from DIRAC                                                         import S_OK, gLogger
from DIRAC.Core.Base.Client                                        import Client
from DIRAC.ConfigurationSystem.Client.Helpers.Operations           import Operations

class ProductionClient( Client ):


  """ Exposes the functionality available in the DIRAC/TransformationHandler
  """
  def __init__( self, **kwargs ):
    """ Simple constructor
    """

    Client.__init__( self, **kwargs )
    self.setServer( 'Production/ProductionManager' )

  def setServer( self, url ):
    self.serverURL = url

  def setName (self, prodName ):
    """
          set the name of the production
    """
    pass

  def addTransformation(self, transID):
    """
          add a transformation to the production
    """
    pass

  def getProductions( self, condDict = None, older = None, newer = None, timeStamp = None,
                          orderAttribute = None, limit = 100, extraParams = False ):
    """ gets all the productions in the system, incrementally. "limit" here is just used to determine the offset.
        for now args are taken from the analogue method 'getTransformations' of the TS
    """
    pass

  def getProduction( self, prodID, extraParams = False ):
    """ gets a specific production.
    """
    pass

  def cleanProduction( self, prodID ):
    """ clean the production, and set the status parameter
    """
    pass

  def deleteProduction(self, prodID):
    """ delete the production from the system
    """
    pass

  def startProduction(self, prodID ):
    """ start the production, and set the status parameter
        There is no analogue in the TS
    """
    pass

  def stopProduction(self, prodID ):
    """ stop the production, and set the status parameter
        There is no analogue in the TSÒ
    """
    pass

  def getProductionTransformations( self, condDict = None, older = None, newer = None, timeStamp = None,
                              orderAttribute = None, limit = 10000, inputVector = False ):
    """ gets all the production transformations for a production, incrementally.
        "limit" here is just used to determine the offset.
    """
    pass






