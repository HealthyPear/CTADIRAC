"""
  Simple Wrapper on the Job class to handle EvnDisp Analysis
"""

__RCSID__ = "$Id$"

# generic imports
import os, json, collections
# DIRAC imports
import DIRAC
from DIRAC.Interfaces.API.Job import Job
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

class EvnDisp3Job( Job ) :
  """ Job extension class for EvnDisp Analysis,
      takes care of running converter and evndisp.
  """
        
  def __init__( self, cpuTime = 432000 ):
    """ Constructor
    
    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
    Job.__init__( self )
    self.setCPUTime( cpuTime )
    # defaults
    self.setName('Evndisplay_Analysis')
    self.package='evndisplay'
    self.version = 'prod3_d20150831b'
    self.layout_list = '3HB1 3HB2 3HB3 3HD1 3HD2 3HI1'
    self.telescopetype_combination_list = 'FA NA FG NG FD ND'
    self.calibration_file = 'prod3.peds.20150820.dst.root'
    self.reconstructionparameter = 'EVNDISP.prod3.reconstruction.runparameter.NN'
    self.NNcleaninginputcard = 'EVNDISP.NNcleaning.dat'
    self.inputpath = './'  ### Update for evndisp!!!
    self.basepath = '/vo.cta.in2p3.fr/MC/PROD3/'
    self.fcc = FileCatalogClient()
    self.metadata = collections.OrderedDict()
    self.filemetadata = {}
    self.jobGroupID = 1

  def setPackage(self, package):
    """ Set package name : e.g. 'evndisplay'
    
    Parameters:
    package -- evndisplay
    """
    self.package=package

  def setVersion(self, version):
    """ Set software version number : e.g. v500-prod3v1
    
    Parameters:
    version -- evndisplay package version number
    """
    self.version=version

  def setLayoutList( self, layout_list ):
    """ Set the layout list

    Parameters:
    layout_list -- list of layouts
    """
    self.layout_list = layout_list

  def setTelescopetypeCombinationList( self, telescopetype_combination_list ):
    """ Set the telescope type combination list

    Parameters:
    telescopetype_combination_list -- list of telescope type combinations
    """
    self.telescopetype_combination_list = telescopetype_combination_list
    
  def setCalibrationFile( self, calibration_file ):
    """ Set the calibration file
    
    Parameters:
    calibration_file -- calibration file name
    """
    self.calibration_file = calibration_file

  def setReconstructionParameter( self, reconstructionparameter ):
    """ Set the reconstruction parameter file
    
    Parameters:
    reconstructionparameter -- parameter file for reconstruction
    """
    self.reconstructionparameter = reconstructionparameter
    
  def setNNcleaninginputcard( self, NNcleaninginputcard ):
    """ Set the cleaning inputcard
    
    Parameters:
    NNcleaninginputcard -- cleaning inputcard
    """
    self.NNcleaninginputcard = NNcleaninginputcard
    
  def setEvnDispMD( self, path ):
    """ Set evndisplay meta data starting from path metadata
    
    Parameters:
    path -- path from which get meta data
    """
    # # Get simtel meta data from path
    res = self.fcc.getFileUserMetadata( path )
    simtelMD = res['Value']

    # # Set evndisp directory meta data
    self.metadata['array_layout'] = simtelMD['array_layout']
    self.metadata['site'] = simtelMD['site']
    self.metadata['particle'] = simtelMD['particle']
    self.metadata['phiP'] = simtelMD['phiP']
    self.metadata['thetaP'] = simtelMD['thetaP']
    # self.metadata['process_program'] = 'evndisp' + '_' + self.version
    self.metadata['analysis_prog'] = 'evndisp'
    self.metadata['analysis_prog_version'] = self.version

    # ## Set file metadata
    # self.filemetadata = {'runNumber': simtelMD['runNumber']}

  def setupWorkflow(self, debug=False):
    """ Setup job workflow by defining the sequence of all executables
        All parameters shall have been defined before that method is called.
    """

    # step 1 -- to be removed -- debug only
    iStep = 1
    if debug:
        lsStep = self.setExecutable( '/bin/ls -alhtr', logFile = 'LS_Init_Log.txt' )
        lsStep['Value']['name']='Step%i_LS_Init'%iStep
        lsStep['Value']['descr_short']='list files in working directory'
        iStep+=1
      
    # step 2  
    swStep = self.setExecutable( '$DIRACROOT/scripts/cta-evndisp-setupsw',
                              arguments='%s %s'% (self.package, self.version),\
                              logFile='SetupSoftware_Log.txt')
    swStep['Value']['name'] = 'Step%i_SetupSoftware' % iStep
    swStep['Value']['descr_short'] = 'Setup software'
    iStep+=1

    # step 2bis
    eivStep = self.setExecutable( '$DIRACROOT/scripts/cta-prod3-verifysteps', \
                              arguments = 'evndispinputs', \
                              logFile = 'Verify_EvnDispInputs_Log.txt' )
    eivStep['Value']['name'] = 'Step%i_VerifyEvnDispInputs' % iStep
    eivStep['Value']['descr_short'] = 'Verify EvnDisp Inputs'
    iStep += 1

    # step 3
    evStep = self.setExecutable( './dirac_evndisp', \
                                arguments = "--layout_list '%s' --telescopetype_combination_list '%s' --calibration_file %s --reconstructionparameter %s --NNcleaninginputcard %s" % ( self.layout_list, self.telescopetype_combination_list, self.calibration_file, self.reconstructionparameter, self.NNcleaninginputcard ), \
                                logFile = 'EvnDisp_Log.txt' )
    evStep['Value']['name'] = 'Step%i_EvnDisplay' % iStep
    evStep['Value']['descr_short'] = 'Run EvnDisplay'
    iStep += 1

    # step 4
    # ## the order of the metadata dictionary is important, since it's used to build the directory structure
    mdjson = json.dumps( self.metadata )

    metadatafield = {'array_layout':'VARCHAR(128)', 'site':'VARCHAR(128)', 'particle':'VARCHAR(128)', \
                         'phiP':'float', 'thetaP': 'float', 'analysis_prog':'VARCHAR(128)', 'analysis_prog_version':'VARCHAR(128)'}

    mdfieldjson = json.dumps( metadatafield )

    fmdjson = json.dumps( self.filemetadata )

    dmStep = self.setExecutable( '$DIRACROOT/CTADIRAC/Core/scripts/cta-evndisp-managedata.py',
                              arguments = "'%s' '%s' '%s' %s %s %s" % ( mdjson, mdfieldjson, fmdjson, self.inputpath, self.basepath, self.jobGroupID ),
                              logFile = 'DataManagement_Log.txt' )
    dmStep['Value']['name'] = 'Step%i_DataManagement' % iStep
    dmStep['Value']['descr_short'] = 'Save files to SE and register them in DFC'
    iStep += 1
