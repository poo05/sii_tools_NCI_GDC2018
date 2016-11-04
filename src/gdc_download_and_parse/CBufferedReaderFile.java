package gdc_download_and_parse;

import java.io.BufferedReader;
import java.util.HashMap;

public class CBufferedReaderFile {
	public BufferedReader buffread;
	public String filename; 
	
	public CBufferedReaderFile(BufferedReader br, String filename){
		buffread = br;
		this.filename = filename;
	}

}
