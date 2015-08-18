knn_result_dir='/mnt/data1/adoni/data/knn_result/'
def validate(attribute,threadhold):
    true=false=0
    for line in open(knn_result_dir+'%s_knn_result.data'%attribute):
        line=line[:-1].split(' ')
        label=int(line[0])
        ratio=float(line[1])
        if ratio>threadhold:
            plabel=0
        elif ratio<threadhold:
            plabel=1
        else:
            continue
        if plabel==label:
            true+=1
        else:
            false+=1
    return true*1.0/(true+false)

def test(attribute):
    print attribute
    max_accuracy=0.0
    for i in xrange(100):
        a=validate(attribute,i*1.0/100)
        if a>max_accuracy:
            max_accuracy=a
    print max_accuracy
    print validate(attribute,-0.5)
    print validate(attribute,1.5)

def main():
    test('gender')
    test('age')
    test('location')
    test('kids')

if __name__=='__main__':
    main()
