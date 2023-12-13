//npm install n3
const fs = require('fs');
const N3 = require('n3');
var zlib = require('node:zlib');


function quad_print(error, quad, prefixes) {
  if (quad) { 
    if (quad.object.value.includes("pubmed.ncbi.nlm.nih.gov") && !(quad.object.value.includes("PMC")))
              console.log(quad.subject.value.split("/").pop().trim(),"\t",quad.object.value.split("/").pop().trim());
  }
}

async function main () {


  
  if (process.argv.length < 3) {
    console.error('Expected at least one argument! <path/pc_reference_identifier_*.ttl.gz> ');
    process.exit(1);
  }
  
  process.argv
  .filter( element => { 
    let suffix = element.split(".").pop();
    return (suffix.toLowerCase() === "gz")||(suffix.toLowerCase() === "ttl") ;
  })
  .forEach(async element => {
    let filePath = element ; 
    let suffix = element.split(".").pop();
    
    if ( suffix.toLowerCase() === "gz" )  {
      filePath = element.replace(".gz","")
      fs.createReadStream(element)
      .pipe(zlib.createGunzip())
      .pipe(fs.createWriteStream(element.replace(".gz","")))
      .on("close", () => {
        const parser = new N3.Parser(), rdfStream = fs.createReadStream(filePath);
        parser.parse(rdfStream, quad_print);
        rdfStream.on("close", () => {
            fs.unlinkSync(filePath);
        });
        
      });
      
    } else {
        const parser = new N3.Parser(), rdfStream = fs.createReadStream(filePath);
        parser.parse(rdfStream, quad_print);
    }
    
  })  
};

main()


