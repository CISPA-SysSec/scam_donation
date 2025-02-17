## Title: Pirates of Charity: Analysis of Donation-based Abuses in Social Media Platforms

## Research Summary
In this research, we analyze donation-based abuses across five social media platforms: X (formerly known as Twitter), Instagram, Telegram, Facebook, and YouTube. This documentation includes the code and data generated to identify fraudulent donation solicitations. The system apparatus requires private API keys, an in-house MongoDB database installation, and several other dependencies listed below. Although, it is not a plug-and-play solution, we aim that our data and code foster future science.

We have two main component as part of the artifacts summary. Below we provide further details.

### Source Code
The first component collects data from various social platforms to identify fraudulent donation solicitations using multiple third-party services. These fraudulent social media profiles are then analyzed based on their profile metadata, such as URLs, phone numbers, and email addresses associated with fraud. The code implementation is available in the ```code/``` directory. Below, we provide key implementations with references to sections of our paper.

|                   Implementation                    |   Paper Section Reference   |                                                                                          Code Reference                                                                                           |
|:---------------------------------------------------:|:---------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|                  Donation Keywords                  |         Section 2.1         |                                                    [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/shared_util.py#L38)                                                    |
|                   Data Collection                   |         Section 2.1         |                                               [link]https://github.com/CISPA-SysSec/scam_donation/blob/main/code/social_media_data_search.py)                                                |
|                   Scam Filtration                   |         Section 2.2         |                                               [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/raw_dataset_filter_logic.py)                                                |
|            Post/Image Clustering             | Section 4, Appendix E and F |                                                       [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/clustering/)                                                        |
|             Scam Data Analysis Analysis             |          Section 5          |                                                       [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/analysis.py)                                                        |
| Fraud Email, Phone Numbers, <br/> and URLs Analysis |          Section 6          | [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/email_and_phone_validate.py), [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/code/virus_total_api.py) |

### Data 

The second component evaluates the raw data collected, delving into the scammer's profile data, fraudulent communication channels (emails, phone numbers, and URLs), and cryptocurrency addresses. In ```data/``` directory we provide the data related to each analysis. Below, we provide key findings with references to sections of our paper.


|                        Findings                         |  Paper Section Reference   |                                                                                                                     Results Reference                                                                                                                      |
|:-------------------------------------------------------:|:--------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| Scam Overview, Profile Creation and Engagement Overview |   Section 3, Appendix C    |                                                                                  [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/profile_meta_data/)                                                                                  |
|               Scammer's Posts Clustering                |        Section 5.3         |                                                                               [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/fraud_clustering/posts/)                                                                                |
|       Evaluation of Fraud Communication Channels        |         Section 4          | [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/fraud_emails/), [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/fraud_phone/), [link](https://github.com/CISPA-SysSec/scam_donation/main/data/fraud_urls/) |
|        Financial Validation and Payment Tracking        | Section 6  |                                                                               [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/fraud_crypto_addresses/)                                                                                |
|           Evaluation of Scammer Profile Image           |         Appendix F         |                                                                               [link](https://github.com/CISPA-SysSec/scam_donation/blob/main/data/fraud_clustering/images/)                                                                               |

## Citation 

```
@inproceedings{acharya_pirates_of_charity_2025,
  author = {Acharya, Bhupendra and Lazzaro, Dario and Emanuele Cinà, Antonio and Holz, Thorsten},
  title = {{Pirates of Charity: Exploring Donation-based Abuses in Social Media Platforms}},
  booktitle="ACM World Wide Web Conference (WWW)",
  year={2025}
 }
```

## Questions and Collaborations

We welcome any questions or discussions to further explore similar attacks on social media. Please feel free to reach out via ```bhupendra.acharya@cispa.de``` or reach out via personal [website](https://bhupendraacharya.com). 


## License
We release our code and data as per MIT License. The copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software. See [License](https://github.com/CISPA-SysSec/scam_donation/blob/main/LICENSE) text for more information.

