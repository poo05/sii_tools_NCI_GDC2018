package gdc_download_and_parse;

import java.util.HashMap;

public class CCmdArgs {
	/**
	 * Command Arguments
	 * 
	 * <P> This class is instantiated and holds the key input arguments as public properties
	 * 
	 *  @author David Schneider
	 *  @version 1.0
	 *  
	 */
	public String inputFolder = "";
	public String outputFolder = "";
	public int collapse = 1;
	public String cohortName = "src";
	public String assembly = "hg38";
	public HashMap<String,String> fileNames = new HashMap<String,String>();
	public int log = 1;
	public int walk = 0;
	public Boolean debug = false;
	
}
