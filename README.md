
# CLI Email Scanner

## Table of Contents

* [About the Project](#About-the-Project)
* [Screenshots](#Screenshots)
* [License](#License)

## About the Project

This project was by client request, to automate their process of receiving emails from employee's and organizing them in the company file system. Utilizing the Gmail API, the process was streamlined into a simple CLI. The email 'From', 'To', 'Subject', and attachments are parsed with a built in text and PDF parser. 

An important part of this project was reorganizing the client file system to allow for a computer friendly interface. The old naming system was inconstant and would occasionally contain typos. This was replaced with a numerical unique ID which was assigned to each project.

The information in the email was automatically matched to the project in the file system. The application downloads the file and places it in the correct folder. Occasionally, information from the PDF is missing and the user is prompted to answer a multiple choice response, to fill in the missing information.

## Screenshots

The main command line interface is used to display a stream of new emails that meet the prerequisite conditions. The user will be prompted by the application with numbered responses, as shown in the example below.


<img src="https://raw.githubusercontent.com/andrew-drogalis/CLI-Email-Scanner/main/screenshots/Email_Scanner.PNG" alt="CLI-Email-
Scanner-Screenshot" style="width: 850px; padding-top: 10px;">


## License

This software is distributed under the GNU license. Please read [LICENSE](https://github.com/andrew-drogalis/CLI-Email-Scanner/blob/main/LICENSE) for information on the software availability and distribution.
