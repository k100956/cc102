 set -ex
      userName=204065533127.dkr.ecr.ap-northeast-1.amazonaws.com
      image=testUser
      version=`cat VERSION`
      echo "version: $version"
      dcker-compose build -t $userName/$image:latest .
      docker tag $userName/$image:latest $userName/$image:$version