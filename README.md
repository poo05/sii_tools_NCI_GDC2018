# sii_tools_NCI_GDC
Processor for handling NCI GDC Data Portal data
/*
How to use

*/

The code expects that the data will be in the following structure

//root/
 /cohortname
  /guidfilenames from .tar.gz for cohort
 somsnp_metadata.[name].json
 cnv_metadata.[name].json
 snv_metadata.[name].json
 gene_expr_metadata.[name].json
 mirna_metadata.[name].json
 clinical.project-[name].json
 biospecimen.project-[name].json
 
 where [name] is some value that is ignored (could be a guid or anything)
 
 
