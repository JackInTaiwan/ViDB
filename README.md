# Hang out with Visual Data: Visual Oriented Database (ViDB)


## Contributors
黃郁珊, 鄭元嘉, 戴若竹, 蕭如芸



<br>

## Description

Why do we improve visual data storage and analysis? Since the bulk of data generated today is unstructured data. To facilitate essential decisions, organizations must discover ways to efficiently manage and analyze unstructured data [1]. Moreover, image analysis plays a significant part in several fields of studies, such as marketing, machine vision, medical scanning, security, etc. Having a well-developed visual-oriented database inevitably has a gradual rise in importance.



<br>

## Outcome

To play with visual data in an elegant manner, we design a visual-oriented database which focuses on image storage, stream process, and ML-based query functionality. The database will be a server with a socket-based interface implemented by Python. To have a picture of it, major features are shown as below.


* Basic Operation
	
    i.Insert instances given file paths or file bytes. We provide three modes to store files: original, compressed and both.

	ii. Delete instances by the id.

	iii. Retrieve instances by the id. The user can specify the mode to retrieve.


* Advanced ML-based Query Operation
    
    i. Query k-nearest instances by visual content/semantic given an instance.
    
    ii. Query k-nearest instances by visual content/semantic given an instance tag.
    
    iii. Query k-nearest instances by visual style/domain given an instance.
    
    iv. Query k-nearest instances by visual style/domain given a style tag.
    
    v. Query k-farthest instances by visual content/semantic given an instance.
    
    vi. Query k-farthest instances by visual style/domain given an instance.
    
    vii. Query similar instances given a group of instances.


* Stream Operation
    
    i. Automatically capture visual frames of interest out of a stream given a “criteria”; specifically, 3 criterion will be provided: CCTV, face recognition, and sports highlights.
    
    ii. When the user applies CCTV criteria, only those frames where people appear will be captured and stored.
    
    iii. When the user applies face recognition criteria, our system will capture those frames where the face of interest appears given a target face in advance.
    
    iv. When the user applies sports highlights criteria, our system will capture those frames considered highlights or moments given the type of sports (e.g., baseball and basketball).



<br>

## Implementation

* Perform Image Compression

    We first transform an image from RGB to YCbCr, which separates the illuminance and the chromatic strength of an image. Since our eyes are more sensitive to illuminance, not to color, a certain percentage of color information can be removed. Besides, we can filter out the high frequency by applying quantization on DCT coefficients of  the image. We can also perform Hoffman encoding to compress data. All these methods help us reduce image resolution while keeping images conservative.

* Query Instances
    Given a target image, we will apply the k-nearest neighbors algorithm (k-NN) to query instances with similar content/style. To be specific, we can apply the Ball Tree algorithm [2] to speed up the query process.

* Extract Distinguishable Image Features
    Given an image to be inserted into the database, we need to save the image and its extracted feature. We will then compare the features to find similar/dissimilar instances.
    i. How to obtain the image feature? We feed the image into an ImageNet pre-trained VGG-16 backbone, and select the output feature map of a specific layer.
    ii. How to compare the content/style similarity between two instance’s features? Following [3], we apply the perceptual loss to compute the content or style loss between two features. For content loss, we simply compute the L2 distance between the two extracted features. On the other hand, to capture style information instead of spatial and structural information, we calculate the Gram matrix of the extracted features. [4]

* Perform Stream Operations
    i. CCTV criteria: motion detection system. We first split the image into grids. Each grid represents an area. We then compute the difference in the same area between different time slots. If the difference is larger than a certain threshold, the motion is detected.
    ii. Face recognition criteria: face recognition system. There are two parts for performing successful face recognition: face detection and face recognition. We can create a face detector with OpenCV. The common choice is a pre-trained “Haar Cascade classifier.” We afterwards put the detected faces into a recognizer to compute their similarity with a target face. We can either train the recognizer by ourselves or use an OpenCV Recognizer.
    iii. Sports highlights criteria: highlight extraction system. We first crawl many web images of sports scenes to fine-tune the Inception Network and use it as a feature extractor. Next, we use the LSTM network to score the extracted feature of each video segment and eventually find the highlight moments.
