package gdc_download_and_parse;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.util.ArrayList;
import java.util.Hashtable;

import org.json.*;


public class CProcessCohort {
	/**
	 * This processes the given cohort (folder)
	 * 
	 * <P> This processes all the records in a cohort
	 * 
	 * <P> It starts with the Clinical file and processes that JSON formatted file
	 * <P> It also stores each case_id-patient_id in a hashtable
	 * <P> This hashtable is used by the otherdata types to lookup the patient_id (since that information is by file_id-case_id)
	 * <P> The hashtable also serves to ensure that if there are two records for a patient, both are not written
	 * <P> This reads in the Clinical file (clinical.project.*) and processes it per the Clinical template ArrayList
	 * 
	 * <P> It also writes out a result file for each datatype, including Clinical, called "_result_[datatype].txt" 
	 * 
	 * <P> It then looks for each datatype list (*_metadata*) and processes each file for that datatype
	 * 
	 * <P> It looks for a filename in the current cohort folder (which is not expected but is handled) and also a folder with the filename
	 * 
	 * <P> If the file is found (either in the current cohort or within a folder), then, if zipped, it unzips it
	 * 
	 * <P> It then checks if the file is a tsv (expected) and if so, appends the necessary extra columns to each row by using the case_id-patient_id hashtable 
	 * 
	 *  @author David Schneider
	 *  @version 1.0
	 *  
	 */
	private Hashtable<String,String> htCasePat;
	// file input/output handling
	private CUtilFileHandling filehandler;

	public CProcessCohort() {
		// hashtable to store case_id-patient_id associations
		htCasePat = new Hashtable<String,String>();
		filehandler = new CUtilFileHandling();
		
	}
	public void Process(CCmdArgs curCmdMap, String curCohort){
		
		// logging handler (java.util.logging)

		
		// look for clinical files
		ArrayList<String> clinicalfiles = filehandler.listFilesAndOrFolders(curCmdMap.inputFolder, "clinical.project", 1, false);
		if (!clinicalfiles.isEmpty()){// we have a metadata clinical file
			for(String curfile: clinicalfiles){
				String curjustfilename = curfile;
				curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
				String jsonFile = filehandler.readFile(curfile);
				jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
				JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
				// process Clinical
				_processClinical(jsonary, curCohort, curCmdMap, curjustfilename);
			}
			
			
		}
		// now let's see if we have metadata files
		ArrayList<String> metadatafiles = filehandler.listFilesAndOrFolders(curCmdMap.inputFolder, "_metadata", 1,false);
		if (!metadatafiles.isEmpty()){// we have metadata files, we can process the cohort
			for(String curfile: metadatafiles){
				// gene expression
				if(curfile.startsWith("gene_expr_metadata")) {
					String curjustfilename = curfile;
					curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
					String jsonFile = filehandler.readFile(curfile);
					jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
					JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
					_processDataType(jsonary, curCohort, curCmdMap, curjustfilename, "general.sample,gene_expr.std", "gene_expr.std", "gene_expr");
				}
				// miRNA
				if(curfile.startsWith("mirna_metadata")) {
					String curjustfilename = curfile;
					curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
					String jsonFile = filehandler.readFile(curfile);
					jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
					JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
					_processDataType(jsonary, curCohort, curCmdMap, curjustfilename, "general.sample,mirna.std", "mirna.std", "mirna");
				}
				// cnv
				if(curfile.startsWith("cnv_metadata")) {
					String curjustfilename = curfile;
					curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
					String jsonFile = filehandler.readFile(curfile);
					jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
					JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
					_processDataType(jsonary, curCohort, curCmdMap, curjustfilename, "general.sample,cnv.std", "cnv.std", "cnv");
				}
				// snp
				if(curfile.startsWith("snp_metadata")) {
					String curjustfilename = curfile;
					curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
					String jsonFile = filehandler.readFile(curfile);
					jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
					JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
					_processDataType(jsonary, curCohort, curCmdMap, curjustfilename, "general.sample,snp.std", "snp.std", "snp");
				}
				// somsnp
				if(curfile.startsWith("somsnp_metadata")) {
					String curjustfilename = curfile;
					curfile = curCmdMap.walk==1?curCmdMap.inputFolder+"/"+curCohort+"/"+curfile:curCmdMap.inputFolder+"/"+curfile;
					String jsonFile = filehandler.readFile(curfile);
					jsonFile = "{\"root\":"+jsonFile+"}";	// deal with vagaries of NCI starting with an array instead of a JSON object
					JSONArray jsonary =  new JSONObject(jsonFile).getJSONArray("root");
					_processDataType(jsonary, curCohort, curCmdMap, curjustfilename, "general.sample,somsnp.std", "somsnp.std", "somsnp");
				}
				
			}
			// process CNV
			
			// process SNV
			// process rppa
		}
	}
	public void _processDataType(JSONArray jsonary,String curCohort, CCmdArgs curCmdMap, String curFile, String headerLine, String dataTypeLine, String outputFileType){
		// process the given file
		String curAssembly = curCmdMap.assembly;
		String outputFile = curCmdMap.inputFolder+"/"+curCmdMap.fileNames.get(outputFileType).split("\\.")[0]+"_"+curCohort+"."+curCmdMap.fileNames.get(outputFileType).split("\\.")[1];

		// generate header row for output
		String header = _getOutputHeaderLine(headerLine); 
		// create file
		BufferedWriter buffwrite = filehandler.openFileForWrite(outputFile, true,  false);
		filehandler.writeLineToBufferedWriter(buffwrite, header, false);
		
		String skipLine = "";
		COutputTemplates coutt = new COutputTemplates();

		// if we are in a line-skip for this type, then skip the line and go to the next
		if(coutt.skiplineTemplate.containsKey(dataTypeLine)) {
			skipLine = coutt.skiplineTemplate.get(dataTypeLine);
		}
		
		
		// process records
		for(int i=0;i<jsonary.length();i++){
			JSONObject curobj = (JSONObject) jsonary.getJSONObject(i);
			// we now check for "case_id" AND also exposures, diagnosis and demographic
			try {
				String file_id = curobj.has("file_id")?curobj.getString("file_id"):"";
				JSONObject ae = curobj.has("associated_entities")? (JSONObject) curobj.getJSONArray("associated_entities").get(0):null;
				if (file_id!="" && ae!=null ){
					if (curCmdMap.debug){System.out.println("Processing: "+ file_id);}
					// now find this file or folder
					CBufferedReaderFile br = filehandler.findAndOpenFileForRead2(curCmdMap.inputFolder+"/"+ file_id, curCmdMap.inputFolder, false);
					if (br!=null){
						// remember that we are passing fileOut to itself on calls other than the first - so do NOT use +=
						String lineOut =_getOutputLine(br.filename+"|"+curFile, curCohort, curAssembly, outputFileType, ae.getString("entity_submitter_id"),ae.getString("entity_submitter_id"), ae, dataTypeLine,"", false);
						String ln = filehandler.readLineFromBufferedReader(br.buffread, false);
						// are we supposed to skip any lines for this type? - we only process if skipLine=="" OR skipLine!="" but the line doesn't start with skipLine value
						while(skipLine!="" && (ln.substring(0, skipLine.length()).equals(skipLine))){
							ln = filehandler.readLineFromBufferedReader(br.buffread, false);
							if (curCmdMap.debug){System.out.println("Skipping line with: "+skipLine );}
						}
						// we want to dynamically check if the first line is a header line or not
						//  we add a header to the output data - in the outputTemplate
						//  so IF the first value for the given datatype = the first value in our retreived line, then it's a header line and we just skip
						if ( (ln.split("\\\t")[0].equals(coutt.outputTemplate.get(dataTypeLine).split(",")[0])) || (ln.split("\\\t")[0].equals("#"+coutt.outputTemplate.get(dataTypeLine).split(",")[0]))) {
							ln = filehandler.readLineFromBufferedReader(br.buffread, false);
						}
						while(ln!=null && ln!=""){
							// handle any specifics by datatype
							String[] correctedLn;
							switch(outputFileType) {
								case "gene_expr": // need ensg by itself AND with version (without .x and just .x)
									correctedLn = ln.split("\t");
									ln = correctedLn[0].split("\\.")[0]+"\t"+correctedLn[0].split("\\.")[1]+"\t"+ correctedLn[1];
									break;
								case "miRNA":	// nothing special - direct copy
									break;
								case "cnv":	// nothing special - direct copy
									break;
								case "somsnp": // we have to process out
									// Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|
									correctedLn = ln.split("\t");
									// position 7 is the info field
									// so we want to split into the above items
									String[] ns = correctedLn[7].split("\\|");
									String n = ns[0] + "\t" + ns[1] + "\t" + ns[2] + "\t" + ns[3] + "\t" + ns[4] + "\t" + ns[5] + "\t" + ns[6] + "\t" + ns[7] + "\t" + ns[8]; 
									
									ln = correctedLn[0] + "\t" + correctedLn[1] +"\t" + correctedLn[2] +"\t" + correctedLn[3] +"\t" + correctedLn[4] +"\t" + correctedLn[5] +"\t"+
											correctedLn[6] +"\t" + n +"\t" + correctedLn[8] +"\t" + correctedLn[9] +"\t" + correctedLn[10];      
									
									break;
								default:
									break;
							}
							lineOut = lineOut.replaceAll("null", " ");

							filehandler.writeLineToBufferedWriter(buffwrite, lineOut +"\t"+ln, false);
							ln = filehandler.readLineFromBufferedReader(br.buffread, false);
						}
						filehandler.readLineFromBufferedReader(br.buffread, true);
					}
				}
			}
			catch(JSONException e) { e.printStackTrace();}
		}
		// close the file
		filehandler.writeLineToBufferedWriter(buffwrite, "", true);

		//filehandler.writeFile(outputFile, false, true, "",true,true);
		if (curCmdMap.debug){System.out.println("Done Processing DataType: "+ outputFileType);}

		
		
	}
	public void _processClinical(JSONArray jsonary, String curCohort, CCmdArgs curCmdMap, String curFile){
		// process the given file
		String curAssembly = curCmdMap.assembly;
		String outputFile = curCmdMap.inputFolder+"/"+curCmdMap.fileNames.get("clinical").split("\\.")[0]+"_"+curCohort+"."+curCmdMap.fileNames.get("clinical").split("\\.")[1];
		
		// NOTE: Clinical files are very short - so we don't worry about just overwriting any existing one
		// generate header row for output
		String header = _getOutputHeaderLine("general.nosample,clinical.demo,clinical.diag,clinical.exps"); 
		// create file 

		BufferedWriter buffwrite = filehandler.openFileForWrite(outputFile, true, false);
		filehandler.writeLineToBufferedWriter(buffwrite, header, false);
		
		// process records
		for(int i=0;i<jsonary.length();i++){
			JSONObject curobj = (JSONObject) jsonary.getJSONObject(i);
			// we now check for "case_id" AND also exposures, diagnosis and demographic
			try {
				String case_id = curobj.has("case_id")?curobj.getString("case_id"):"";
				JSONObject demo = curobj.has("demographic")? curobj.getJSONObject("demographic"):null;
				JSONObject diag = curobj.has("diagnoses")?  (JSONObject) curobj.getJSONArray("diagnoses").get(0) : null;
				JSONObject exps = curobj.has("exposures")? (JSONObject) curobj.getJSONArray("exposures").get(0): null;
				if (case_id!="" && demo!=null && diag!=null && exps!=null){
					// cases are supposed to be unique - so we won't add a case twice to the hashmap
					if (!htCasePat.containsKey(case_id)){
						// remember that we are passing fileOut to itself on calls other than the first - so do NOT use +=
						String lineOut =_getOutputLine(curFile, curCohort, curAssembly, "clinical", demo.getString("submitter_id"),"", demo, "clinical.demo","", false);
						lineOut = _getOutputLine(curFile, curCohort, curAssembly, "clinical", demo.getString("submitter_id"),"", diag, "clinical.diag",lineOut, true);
						lineOut = _getOutputLine(curFile, curCohort, curAssembly, "clinical", demo.getString("submitter_id"),"", exps, "clinical.exps",lineOut, true);
						
						lineOut = lineOut.replaceAll("null", " ");
						// track case_id-patient_id
						htCasePat.put(case_id,demo.getString("submitter_id").substring(0, 12));

						// output
						filehandler.writeLineToBufferedWriter(buffwrite, lineOut, false);
					}
				}
			}
			catch(JSONException e) { System.out.println("exception");}
		}
		// close the file
		filehandler.writeLineToBufferedWriter(buffwrite, "", true);

	}
	public String _getOutputLine(String curFile, String curCohort, String curAssembly, String dataType, String submitter, String sample
			, JSONObject curObj, String templateName, String prevLine, Boolean continueLine){
		COutputTemplates outputTemplates = new COutputTemplates();

		String rtn = continueLine ? prevLine : _getLineStart(curFile, curCohort, curAssembly, dataType, submitter,sample);
		String[] tParams = outputTemplates.outputTemplate.get(templateName).split(",");
		for(int j=0;j < tParams.length ;j++){
			String curParam = tParams[j].contains("|")?tParams[j].split("\\|")[0]:tParams[j];
			if(curObj.has(curParam)) {
				rtn+="\t" + (String)(curObj.isNull(curParam)?"":curObj.get(curParam).toString());
			}
		}
		return rtn;
	}
	public String _getOutputHeaderLine(String headersToUse){
		String rtn = "";
		COutputTemplates outputTemplates = new COutputTemplates();
		String[] headerAry = headersToUse.split(",");
		
		for(int j=0;j<headerAry.length;j++){
			String[] tHeader = outputTemplates.outputTemplate.get(headerAry[j]).split(",");
			for(int k=0;k<tHeader.length;k++){
				rtn += 
					(tHeader[k].contains("|")?tHeader[k].split("\\|")[1]:tHeader[k])
					+ ((j==headerAry.length && k==tHeader.length)?"":"\t");
					}
		}
		return rtn;
	}
	public String _getLineStart(String curFile, String curCohort, String curAssembly, String dataType, String submitter, String sample){
		String rtn = curCohort+"\t"+curAssembly+"\t"+dataType+"\t"+submitter.substring(0, 12);
		if(sample!=""){ // include sample type and sample
			rtn += "\t"+sample.substring(13,15)+"\t"+sample.substring(13);
		}
		return rtn;
	}

}
