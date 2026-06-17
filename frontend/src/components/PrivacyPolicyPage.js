import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield, Mail } from 'lucide-react';

const PrivacyPolicyPage = () => {
  const lastUpdated = "18 February 2025";
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-900 text-white py-16">
        <div className="max-w-4xl mx-auto px-6">
          <Link to="/" className="inline-flex items-center text-blue-300 hover:text-white mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center space-x-4 mb-4">
            <Shield className="w-12 h-12 text-blue-400" />
            <h1 className="text-4xl md:text-5xl font-bold">Privacy Policy</h1>
          </div>
          <p className="text-slate-300">
            Last updated: {lastUpdated}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <div className="bg-white rounded-xl p-8 md:p-12 shadow-lg prose prose-slate max-w-none">
          
          {/* POPIA Compliance Notice */}
          <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded-r-lg mb-8 not-prose">
            <h3 className="text-lg font-bold text-blue-800 mb-2">POPIA Compliance</h3>
            <p className="text-blue-700 text-sm">
              This Privacy Policy complies with the Protection of Personal Information Act 4 of 2013 (POPIA) 
              of South Africa. Job Rocket (Pty) Ltd is committed to protecting your personal information 
              and your right to privacy.
            </p>
          </div>

          <h2>1. Introduction</h2>
          <p>
            Job Rocket (Pty) Ltd ("Job Rocket", "we", "us", or "our") is committed to protecting your personal 
            information. This Privacy Policy explains how we collect, use, store, share, and protect your 
            personal information in accordance with the Protection of Personal Information Act 4 of 2013 (POPIA) 
            and other applicable South African laws.
          </p>
          <p>
            By using our website and services at jobrocket.co.za, you consent to the collection and use of 
            your personal information as described in this policy.
          </p>

          <h2>2. Responsible Party</h2>
          <p>
            The responsible party for the processing of your personal information is:
          </p>
          <div className="bg-slate-50 p-4 rounded-lg not-prose mb-6">
            <p className="font-semibold">Job Rocket (Pty) Ltd</p>
            <p>Johannesburg, Gauteng, South Africa</p>
            <p>Email: <a href="mailto:privacy@jobrocket.co.za" className="text-blue-600">privacy@jobrocket.co.za</a></p>
          </div>

          <h2>3. Information We Collect</h2>
          <p>We collect and process the following categories of personal information:</p>
          
          <h3>3.1 Information You Provide Directly</h3>
          <ul>
            <li><strong>Identity Information:</strong> Name, surname, ID number (optional), date of birth</li>
            <li><strong>Contact Information:</strong> Email address, phone number, physical address</li>
            <li><strong>Professional Information:</strong> CV/resume, work history, education, skills, qualifications</li>
            <li><strong>Account Information:</strong> Username, password (encrypted), account preferences</li>
            <li><strong>Company Information:</strong> (For recruiters) Company name, registration details, company description</li>
          </ul>

          <h3>3.2 Information Collected Automatically</h3>
          <ul>
            <li><strong>Technical Data:</strong> IP address, browser type, device information</li>
            <li><strong>Usage Data:</strong> Pages visited, time spent on pages, click patterns</li>
            <li><strong>Cookies:</strong> Session cookies and persistent cookies (see Section 9)</li>
          </ul>

          <h2>4. Purpose of Processing</h2>
          <p>We process your personal information for the following purposes:</p>
          <ul>
            <li>To create and manage your user account</li>
            <li>To facilitate job applications and recruitment processes</li>
            <li>To match job seekers with relevant job opportunities</li>
            <li>To enable communication between job seekers and recruiters</li>
            <li>To process payments for subscription services</li>
            <li>To send job alerts and notifications (with your consent)</li>
            <li>To improve our services and user experience</li>
            <li>To comply with legal obligations</li>
            <li>To prevent fraud and ensure platform security</li>
          </ul>

          <h2>5. Legal Basis for Processing</h2>
          <p>Under POPIA, we process your personal information based on one or more of the following grounds:</p>
          <ul>
            <li><strong>Consent:</strong> You have given us explicit consent to process your information</li>
            <li><strong>Contract:</strong> Processing is necessary for us to fulfill our agreement with you</li>
            <li><strong>Legal Obligation:</strong> We are required by law to process your information</li>
            <li><strong>Legitimate Interest:</strong> Processing is in our legitimate business interests and does not unduly affect your rights</li>
          </ul>

          <h2>6. Sharing of Personal Information</h2>
          <p>We may share your personal information with:</p>
          <ul>
            <li><strong>Employers/Recruiters:</strong> When you apply for jobs, your profile and application information is shared with the relevant employer</li>
            <li><strong>Service Providers:</strong> Third parties who assist in operating our platform (payment processors, hosting providers, email services)</li>
            <li><strong>Legal Authorities:</strong> When required by law or to protect our legal rights</li>
          </ul>
          <p>
            We do not sell your personal information to third parties. All third-party service providers are 
            contractually bound to protect your information in accordance with POPIA.
          </p>

          <h2>7. Cross-Border Transfers</h2>
          <p>
            Your personal information may be transferred to and processed in countries outside South Africa. 
            In such cases, we ensure that:
          </p>
          <ul>
            <li>The recipient country has adequate data protection laws, or</li>
            <li>We have binding agreements in place that provide equivalent protection</li>
            <li>You have consented to such transfer</li>
          </ul>

          <h2>8. Data Retention</h2>
          <p>We retain your personal information for as long as:</p>
          <ul>
            <li>Your account remains active</li>
            <li>Necessary to provide you with our services</li>
            <li>Required by law (e.g., financial records: 5 years)</li>
            <li>Needed to resolve disputes or enforce agreements</li>
          </ul>
          <p>
            Inactive accounts may be deleted after 24 months of inactivity. You may request deletion of your 
            account and personal information at any time (see Section 10).
          </p>

          <h2>9. Cookies and Tracking Technologies</h2>
          <p>Our website uses cookies to:</p>
          <ul>
            <li>Keep you signed in to your account</li>
            <li>Remember your preferences</li>
            <li>Analyse website traffic and usage patterns</li>
            <li>Improve website functionality</li>
          </ul>
          <p>
            You can manage cookie preferences through your browser settings. Note that disabling cookies may 
            affect website functionality.
          </p>

          <h2>10. Your Rights Under POPIA</h2>
          <p>As a data subject, you have the following rights:</p>
          <ul>
            <li><strong>Right to Access:</strong> Request confirmation of whether we hold your personal information and access to such information</li>
            <li><strong>Right to Correction:</strong> Request correction of inaccurate, irrelevant, or outdated personal information</li>
            <li><strong>Right to Deletion:</strong> Request deletion of your personal information (subject to legal retention requirements)</li>
            <li><strong>Right to Object:</strong> Object to the processing of your personal information on reasonable grounds</li>
            <li><strong>Right to Withdraw Consent:</strong> Withdraw consent previously given for processing</li>
            <li><strong>Right to Lodge a Complaint:</strong> Lodge a complaint with the Information Regulator</li>
          </ul>

          <p>To exercise any of these rights, contact us at:</p>
          <div className="bg-slate-50 p-4 rounded-lg not-prose mb-6">
            <p>Email: <a href="mailto:privacy@jobrocket.co.za" className="text-blue-600">privacy@jobrocket.co.za</a></p>
            <p>Subject Line: "POPIA Request - [Your Request Type]"</p>
            <p className="text-sm text-slate-600 mt-2">
              We will respond to your request within 30 days as required by POPIA.
            </p>
          </div>

          <h2>11. Security Measures</h2>
          <p>We implement appropriate technical and organisational measures to protect your personal information, including:</p>
          <ul>
            <li>Encryption of data in transit and at rest</li>
            <li>Secure password hashing</li>
            <li>Regular security assessments</li>
            <li>Access controls and authentication</li>
            <li>Employee training on data protection</li>
          </ul>
          <p>
            While we take all reasonable steps to protect your information, no internet transmission is 
            completely secure. We cannot guarantee absolute security.
          </p>

          <h2>12. Information Regulator</h2>
          <p>
            If you believe your privacy rights have been violated, you have the right to lodge a complaint 
            with the Information Regulator:
          </p>
          <div className="bg-slate-50 p-4 rounded-lg not-prose mb-6">
            <p className="font-semibold">The Information Regulator (South Africa)</p>
            <p>JD House, 27 Stiemens Street, Braamfontein, Johannesburg, 2001</p>
            <p>P.O Box 31533, Braamfontein, Johannesburg, 2017</p>
            <p>Email: <a href="mailto:complaints.IR@justice.gov.za" className="text-blue-600">complaints.IR@justice.gov.za</a></p>
          </div>

          <h2>13. Children's Privacy</h2>
          <p>
            Our services are not intended for persons under the age of 18. We do not knowingly collect 
            personal information from children. If we become aware that a child has provided us with 
            personal information, we will delete such information.
          </p>

          <h2>14. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. Material changes will be communicated 
            via email or a prominent notice on our website. Continued use of our services after changes 
            constitutes acceptance of the updated policy.
          </p>

          <h2>15. Contact Us</h2>
          <p>For any questions about this Privacy Policy or our privacy practices, contact us at:</p>
          <div className="bg-blue-50 p-6 rounded-lg not-prose">
            <div className="flex items-center space-x-3 mb-2">
              <Mail className="w-5 h-5 text-blue-600" />
              <a href="mailto:privacy@jobrocket.co.za" className="text-blue-600 font-semibold">privacy@jobrocket.co.za</a>
            </div>
            <p className="text-sm text-slate-600">
              We aim to respond to all privacy-related enquiries within 48 hours.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
