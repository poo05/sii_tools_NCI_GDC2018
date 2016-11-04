package gdc_download_and_parse;

import java.util.HashMap;

// this class defines the output templates for data output into tsv's from the input source
// this class is consumed by the processor class(es) 
public class COutputTemplates {
	/**
	 * Output Templates
	 * 
	 * <P> Various templates used by the Process class(es) to output tsv files
	 * 
	 * <P> The templates are NOT classes - they are arrays of strings which we want to and expect to find in the JSON.
	 * 
	 * <P> We do NOT want to add any additional fields that aren't expected because that would change the output and downstream consumers would have to then identify and handle these exceptions
	 * 
	 * <P> We want to add ALL of the expected fields because that ensures that downstream consumers can blindly read the data without analysis/pre-handling
	 * 
	 * <P> The reason we do not use a JSON->TSV library is that we are (a) heavily modifying the output - combining multiple sections in the JSON into a flat tsv AND (b) we are also appending new elements to the tsv
	 * 
	 * <P> Each field can have a translated field value - just add a | (pipe) character - the first value is the field and the second is what will be written as a header for the 'column'
	 * 
	 *  @author David Schneider
	 *  @version 1.0
	 *  
	 */
	
	public static HashMap<String,String> outputTemplate = new HashMap<String,String>();
	
	public COutputTemplates() {
		outputTemplate.put("general.nosample", "cohort,assembly,data_type,patient_id");
		outputTemplate.put("general.sample", "cohort,assembly,data_type,patient_id,sample_type,sample_id");

		outputTemplate.put("clinical.demo", "gender,state|demographic_state,year_of_birth,race,ethnicity,year_of_death");
		outputTemplate.put("clinical.diag", "classification_of_tumor,last_known_disease_status,primary_diagnosis,tumor_stage,age_at_diagnosis,vital_status,morphology,days_to_death,days_to_last_known_disease_status,days_to_last_follow_up,state,days_to_recurrence,diagnosis_id,tumor_grade,tissue_or_organ_of_origin,days_to_birth,progression_or_recurrence,prior_malignancy,site_of_resection_or_biopsy");
		outputTemplate.put("clinical.exps", "cigarettes_per_day,weight,alcohol_history,alcohol_intensity,bmi,years_smoked,height,state|exposure_state");
		
		outputTemplate.put("mirna.std", "miRNA_ID,read_count,reads_per_million_miRNA_mapped,cross-mapped");
		outputTemplate.put("gene_expr.std", "ensg_id,ensg_id_ver,fpkm_norm_by_genelength");
		
	}
	
}
