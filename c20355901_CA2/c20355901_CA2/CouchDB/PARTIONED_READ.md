Add a view and use this one for checking fact and dim tables with partions

function(doc) {
    if (doc.type === 'dim' && doc.dim_data.AGE_GROUP_DESC === '>50') {
        emit(doc._id, doc);
    } else if (doc.type === 'fact' && doc.data.VOTECATEGORY === 'Jury') {
        emit(doc._id, doc);
    }
  
}