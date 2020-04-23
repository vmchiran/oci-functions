# oci-objectstorage-list-objects-python
Ref. https://github.com/oracle/oracle-functions-samples/tree/master/oci-objectstorage-list-objects-python

    cd oci-objectstorage-list-objects-python
    fn -v deploy --app vch-helloworld-app

    echo -n '{"bucketName": "oic-bucket"}' | fn invoke vch-helloworld-app oci-objectstorage-list-objects-python