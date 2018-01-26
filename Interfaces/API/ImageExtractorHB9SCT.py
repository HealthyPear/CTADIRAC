"""
  Wrapper on the Job class to handle ImageExtractor DL0->DL1 reduction of SCTs HB9
"""

__RCSID__ = "$Id$"

# generic imports
import json
import collections
# DIRAC imports
import DIRAC
from DIRAC.Interfaces.API.Job import Job
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

class ImageExtractorHB9SCT(Job) :
    """ Job extension class for ImageExtractor DL0->DL1 reduction of HB9 SCT
      takes care of running SCT extraction and merging, and DL0->DL1 HDF5
      conversion for Machine Learning fans
    """

    def __init__(self, cpuTime=36000):
    """ Constructor

    Keyword arguments:
    cpuTime -- max cpu time allowed for the job
    """
    Job.__init__(self)
    self.setCPUTime(cpuTime)
    # defaults
    self.setName('ImageExtractor reduction')
    self.package='image_extractor'
    self.program_category='calibimgreco'
    self.version = 'v0.5.1'
    self.configuration_id = -1
    self.output_data_level=1
    self.prefix = 'CTA.prod3Sb'
    self.layout = 'HB9'
    self.basepath = '/vo.cta.in2p3.fr/MC/PROD3/'
    self.outputpattern = './*.hdf5'
    self.fcc = FileCatalogClient()
    self.metadata = collections.OrderedDict()
    self.filemetadata = {}
    self.catalogs = json.dumps(['DIRACFileCatalog','TSCatalog'])

    def setTSTaskId(self, taskid):
    """ Set TS task Id, dynamically resolved at job run time

    Parameters:
    taskid -- an int
    """
    self.ts_task_id=taskid

    def setPackage(self, package):
        """ Set package name : e.g. 'image_extractor'

        Parameters:
        package -- image_extractor
        """
        self.package=package

    def setVersion(self, version):
        """ Set software version number : e.g. v0.5.1

        Parameters:
        version -- image extractor package version number
        """
        self.version=version

    def setPrefix(self, prefix):
        """ Set prefix for layout name

        Parameters:
        prefix -- prefix for layout names
        """
        self.prefix = prefix

    def setLayout(self, layout):
        """ Set the layout list

        Parameters:
        layout -- the layout "Baseline"
        """
        self.layout = layout

    def set_ie_metadata( self, path ):
        """ Set image_extractor meta data starting from path metadata

        Parameters:
        path -- path from which get meta data
        """
        # # Get simtel meta data from path
        res = self.fcc.getFileUserMetadata( path )
        simtelMD = res['Value']
        # set directory meta data
        self.metadata['array_layout'] = simtelMD['array_layout']
        self.metadata['site'] = simtelMD['site']
        self.metadata['particle'] = simtelMD['particle']
        self.metadata['phiP'] = simtelMD['phiP']['=']
        self.metadata['thetaP'] = simtelMD['thetaP']['=']
        self.metadata[self.program_category+'_prog'] = self.package
        self.metadata[self.program_category+'_prog_version'] = self.version
        self.metadata['data_level'] = self.output_data_level
        self.metadata['configuration_id'] = self.configuration_id
        # here hardcode that we have SCTs
        self.metadata['sct'] = 'True'
        print(self.metadata)

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
        swStep = self.setExecutable( '$DIRACROOT/scripts/cta-prod3-setupsw',
                                  arguments='%s %s'% (self.package, self.version),\
                                  logFile='SetupSoftware_Log.txt')
        swStep['Value']['name'] = 'Step%i_SetupSoftware' % iStep
        swStep['Value']['descr_short'] = 'Setup software'
        iStep+=1

        # step 2bis
        # arguments are nbFiles=0 (not used) and fileSize=100kB
        eivStep = self.setExecutable( '$DIRACROOT/scripts/cta-prod3-verifysteps', \
                                  arguments = 'analysisinputs 0 100', \
                                  logFile = 'Verify_EvnDispInputs_Log.txt' )
        eivStep['Value']['name'] = 'Step%i_VerifyEvnDispInputs' % iStep
        eivStep['Value']['descr_short'] = 'Verify EvnDisp Inputs'
        iStep += 1

        # step 3 - download SCT files corresponding to no-SCT merged input
        #    rctaStep = self.setExecutable( 'python ./cta-prod3-get-matching-data.py HB9SCT',\
        #    rctaStep = self.setExecutable( '$DIRACROOT/scripts/cta-prod3-get-matching-data HB9SCT',\
        rctaStep = self.setExecutable( 'python ./cta-prod3-get-matching-data.py HB9SCT',\
                                    logFile = 'Download_Files_Log.txt' )
        rctaStep['Value']['name'] = 'Step%i_Download_Files' % iStep
        rctaStep['Value']['descr_short'] = 'Download SCT Files'
        iStep += 1

        # step 4 -- arguments hard coded !
        evStep = self.setExecutable( './dirac_prod3b_evndisp_SCT',
                                    logFile = 'EvnDisp_SCT_Log.txt' )
        evStep['Value']['name'] = 'Step%i_EvnDisplay' % iStep
        evStep['Value']['descr_short'] = 'Run EvnDisplay'
        iStep += 1

        # step 5
        # ## the order of the metadata dictionary is important, since it's used to build the directory structure
        mdjson = json.dumps( self.metadata )

        metadatafield = {'array_layout':'VARCHAR(128)', 'site':'VARCHAR(128)', 'particle':'VARCHAR(128)', \
                         'phiP':'float', 'thetaP': 'float', \
                         'analysis_prog':'VARCHAR(128)', 'analysis_prog_version':'VARCHAR(128)'}

        mdfieldjson = json.dumps( metadatafield )

        fmdjson = json.dumps( self.filemetadata )

        # register Data
        self.outputpattern = './*SCT_evndisp.tar'
        dmStep = self.setExecutable( '$DIRACROOT/CTADIRAC/Core/scripts/cta-analysis-managedata.py',
                                  arguments = "'%s' '%s' '%s' %s '%s' %s" % ( mdjson, mdfieldjson, fmdjson, self.basepath, self.outputpattern, self.package ),
                                  logFile = 'Data_DataManagement_Log.txt' )
        dmStep['Value']['name'] = 'Step%i_Data_DataManagement' % iStep
        dmStep['Value']['descr_short'] = 'Save data files to SE and register them in DFC'
        iStep += 1

        # register Log
        self.outputpattern = './*SCT_evndisp.logs.tar'
        dmStep = self.setExecutable( '$DIRACROOT/CTADIRAC/Core/scripts/cta-analysis-managedata.py',
                                  arguments = "'%s' '%s' '%s' %s '%s' %s" % ( mdjson, mdfieldjson, fmdjson, self.basepath, self.outputpattern, self.package ),
                                  logFile = 'Log_DataManagement_Log.txt' )
        dmStep['Value']['name'] = 'Step%i_Log_DataManagement' % iStep
        dmStep['Value']['descr_short'] = 'Save log files to SE and register them in DFC'
        iStep += 1
