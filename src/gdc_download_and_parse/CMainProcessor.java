package gdc_download_and_parse;

import java.util.ArrayList;

public class CMainProcessor {
	/**
	 * The Main Processor
	 * 
	 * <P> This processes the request from MAIN
	 * 
	 * <P> It will either process all the files in a folder or a single folder
	 * 
	 * <P> See the command parameter arguments for more details (usage)
	 * 
	 *  @author David Schneider
	 *  @version 1.0
	 *  
	 */
	public void Process(CCmdArgs curCmdMap){
		// let's see where we are
		// if walk=1 then we want to see if we have a list of folders that look like cohorts 
		// if walk=0 then we want to see if we have any metadata files
		CUtilFileHandling filehandler = new CUtilFileHandling();
		
		CProcessCohort procCohort = new CProcessCohort();
		
		ArrayList<String> folderList = null,
				fileList = null;
		String curCohort = "";
		
		if(curCmdMap.walk==1){
			folderList = filehandler.listFilesAndOrFolders(curCmdMap.inputFolder, "", 2, false);
			if(!folderList.isEmpty()){
				// walk the folders and process each
				for(String thisCohort: folderList){
					procCohort.Process(curCmdMap,thisCohort);
				}
			}
		}
		else { // we should be IN a folder currently - so get the name of the search folder and get the cohort name from that
			curCohort = curCmdMap.inputFolder.substring(curCmdMap.inputFolder.lastIndexOf("/")+1);
			procCohort.Process(curCmdMap,curCohort);
		}
		
		
		
		
	}

}
