
// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXMoleculeSet.h"

namespace Nanorex {

unsigned int NXMoleculeSet::NextMoleculeIndex = 0;


/* CONSTRUCTOR */
NXMoleculeSet::NXMoleculeSet() {
}


/* DESTRUCTOR */
NXMoleculeSet::~NXMoleculeSet() {
	// TODO: Recursively delete sub-NXMSs
}


/* FUNCTION: newMolecule */
OBMol* NXMoleculeSet::newMolecule() {
	OBMol* molecule = new OBMol();
	NXMoleculeData* moleculeData = new NXMoleculeData();
	moleculeData->SetIdx(NextMoleculeIndex);
	NextMoleculeIndex++;
	molecule->SetData(moleculeData);
	molecules.push_back(molecule);
	return molecule;
}


/* FUNCTION: getCounts */
void NXMoleculeSet::getCounts(unsigned int& moleculeCount,
							  unsigned int& atomCount,
							  unsigned int& bondCount) {
							  
	moleculeCount = atomCount = bondCount = 0;
	getCountsHelper(moleculeCount, atomCount, bondCount, this);
}


/* FUNCTION: getCountsHelper */
void NXMoleculeSet::getCountsHelper(unsigned int& moleculeCount,
									unsigned int& atomCount,
									unsigned int& bondCount,
									NXMoleculeSet* moleculeSet) {
									
	moleculeCount += moleculeSet->moleculeCount();
	OBMolIterator moleculeIter = moleculeSet->moleculesBegin();
	while (moleculeIter != moleculeSet->moleculesEnd()) {
		atomCount += (*moleculeIter)->NumAtoms();
		bondCount += (*moleculeIter)->NumBonds();
		moleculeIter++;
	}
	NXMoleculeSetIterator moleculeSetIter = moleculeSet->childrenBegin();
	while (moleculeSetIter != moleculeSet->childrenEnd()) {
		getCountsHelper(moleculeCount, atomCount, bondCount, *moleculeSetIter);
		moleculeSetIter++;
	}
}


} // Nanorex::
