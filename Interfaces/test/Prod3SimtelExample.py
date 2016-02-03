""" Prod3 MC Script to run simtel_array for a given configuration
"""

from DIRAC.Core.Base import Script
Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s corsika input file list' % Script.scriptName,
                                     'Arguments:',
                                     '  inputfiles: corsika input file list',
                                     '\ne.g: %s corsika.list' % Script.scriptName,
                                     ] ) )

Script.parseCommandLine()

import DIRAC
from CTADIRAC.Interfaces.API.Prod3MCUserJob import Prod3MCUserJob
from DIRAC.Interfaces.API.Dirac import Dirac

def submitWMS( job, infileList, nbFileperJob ):
  """ Submit the job locally or to the WMS  """

  dirac = Dirac()
  res = Dirac().splitInputData( infileList, nbFileperJob )
  if not res['OK']:
    Script.gLogger.error( 'Failed to splitInputData' )
    DIRAC.exit( -1 )

  job.setGenericParametricInput( res['Value'] )
  job.setInputData( '%s' )
  job.setOutputData( ['*simtel.gz'] )

  res = dirac.submit( job )

  Script.gLogger.info( 'Submission Result: ', res['Value'] )
  return res



def runProd3( args = None ):
  """ Simple wrapper to create a Prod3MCUserJob and setup parameters
      from positional arguments given on the command line.
      
      Parameters:
      args -- corsika input file list
  """

  # get arguments
  infile = args[0]
  f = open( infile, 'r' )

  infileList = []
  for line in f:
    infile = line.strip()
    if line != "\n":
      infileList.append( infile )

  ### Main script
  job = Prod3MCUserJob()
  job.setName( 'simteljob' )

  # set package version: to be set before setupWorkflow
  job.setPackage('corsika_simhessarray')
  job.setVersion( '2015-10-20-p3' )

  ## set sim_telarray config
  job.setSimtelCfg( 'mycfg/CTA-ULTRA6-SST-GCT-S.cfg' )
  #job.setSimtelOpts('TELESCOPE_THETA=20.0 TELESCOPE_PHI=90.0') ## optional

  ## set job attributes
  job.setOutputSandbox( ['*Log.txt'] )
  job.setInputSandbox( ['mycfg'] )

  # ## setup workflow: set executable and parameters
  job.setupWorkflow()

  ## group input files and submit
  res = submitWMS( job, infileList, 2 )

  # debug
    #Script.gLogger.info( job.workflow )

  return res

#########################################################
if __name__ == '__main__':

  args = Script.getPositionalArgs()
  if ( len( args ) != 1 ):
    Script.showHelp()
  try:
    res = runProd3( args )
    if not res['OK']:
      DIRAC.gLogger.error ( res['Message'] )
      DIRAC.exit( -1 )
    else:
      DIRAC.gLogger.notice( res['Value'] )
  except Exception:
    DIRAC.gLogger.exception()
    DIRAC.exit( -1 )
