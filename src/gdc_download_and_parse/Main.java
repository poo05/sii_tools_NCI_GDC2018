package gdc_download_and_parse;

import java.util.HashMap;
import java.util.Map;

import ca.zmatrix.cli.ParseCmd;



public class Main {
	public static void main(String[] args){
		System.out.println("hi there !  hello!");
		
		String usage = "usage -i [inputfolder] -o [outputfolder, defaults to same cohort folder]"
				+ " -collapse [collapse subfolders with data into cohort folder, 0 or 1, defaults to 1]"
				+ " -cohortname [the name of the cohort to use, src or value, defaults to src]"
				+ " -walk [walk the given folder for cohorts?  0 or 1, defaults to 0]";
				
		
		ParseCmd cmd = new ParseCmd.Builder()
				.help(usage)
				.parm("-i", "").req()
				.parm("-o", "")
				.parm("-collapse", "1")
				.parm("-cohortname","src")
				.parm("-walk","0")
				.parm("-assembly","hg38")
				.parm("-log","1")
				.parm("-filenames","clinical=clinical.tsv;mirna=mirna.tsv;gene_expr=gene_expr.tsv")
				.parm("-debug","0")
				.build();
		Map<String,String> cmdMap = new HashMap<String,String>();
		String parsingErr = cmd.validate(args);
		if (cmd.isValid(args)){
			cmdMap = cmd.parse(args);

			CCmdArgs cmdArgs = new CCmdArgs();
			cmdArgs.inputFolder = cmdMap.get("-i");
			cmdArgs.outputFolder = cmdMap.get("-o");
			cmdArgs.cohortName = cmdMap.get("-cohortname");
			cmdArgs.collapse = Integer.parseInt(cmdMap.get("-collapse"));
			cmdArgs.walk = Integer.parseInt(cmdMap.get("-walk"));
			cmdArgs.assembly = cmdMap.get("-assembly");
			cmdArgs.log =  Integer.parseInt(cmdMap.get("-log"));
			cmdArgs.debug = (cmdMap.get("-debug")=="1" || Integer.parseInt(cmdMap.get("-debug"))==1)  ?true:false;
			String rawFilenames = cmdMap.get("-filenames");
			
			String[] filenamesMap = rawFilenames.split(";");
			for(int i=0;i<filenamesMap.length;i++){
				cmdArgs.fileNames.put(filenamesMap[i].split("=")[0],filenamesMap[i].split("=")[1]);
			}
			
			CMainProcessor mainproc = new CMainProcessor();
			mainproc.Process(cmdArgs);
		}
		else {System.out.println(parsingErr); System.exit(-10);}
	}

}
