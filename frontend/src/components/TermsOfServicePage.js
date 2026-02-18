import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText, Mail } from 'lucide-react';

const TermsOfServicePage = () => {
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
            <FileText className="w-12 h-12 text-blue-400" />
            <h1 className="text-4xl md:text-5xl font-bold">Terms of Service</h1>
          </div>
          <p className="text-slate-300">
            Last updated: {lastUpdated}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <div className="bg-white rounded-xl p-8 md:p-12 shadow-lg prose prose-slate max-w-none">
          
          {/* Important Notice */}
          <div className="bg-amber-50 border-l-4 border-amber-500 p-6 rounded-r-lg mb-8 not-prose">
            <h3 className="text-lg font-bold text-amber-800 mb-2">Important</h3>
            <p className="text-amber-700 text-sm">
              Please read these Terms of Service carefully before using our platform. By accessing or using 
              Job Rocket, you agree to be bound by these terms. If you do not agree, please do not use our services.
            </p>
          </div>

          <h2>1. Introduction and Acceptance</h2>
          <p>
            These Terms of Service ("Terms") constitute a legally binding agreement between you and Job Rocket 
            (Pty) Ltd ("Job Rocket", "we", "us", or "our"), a company registered in the Republic of South Africa.
          </p>
          <p>
            By creating an account, accessing, or using our website at jobrocket.co.za and related services 
            (collectively, the "Platform"), you acknowledge that you have read, understood, and agree to be 
            bound by these Terms, our <Link to="/privacy-policy">Privacy Policy</Link>, and any other policies 
            referenced herein.
          </p>
          <p>
            These Terms are governed by the laws of the Republic of South Africa, including but not limited to:
          </p>
          <ul>
            <li>The Consumer Protection Act 68 of 2008 (CPA)</li>
            <li>The Electronic Communications and Transactions Act 25 of 2002 (ECTA)</li>
            <li>The Protection of Personal Information Act 4 of 2013 (POPIA)</li>
            <li>The Labour Relations Act 66 of 1995</li>
          </ul>

          <h2>2. Definitions</h2>
          <p>In these Terms, unless the context indicates otherwise:</p>
          <ul>
            <li><strong>"Job Seeker"</strong> means any individual who registers on the Platform to search for employment opportunities</li>
            <li><strong>"Recruiter"</strong> or <strong>"Employer"</strong> means any company, organisation, or individual who registers on the Platform to advertise job opportunities</li>
            <li><strong>"User"</strong> means any Job Seeker, Recruiter, or visitor to the Platform</li>
            <li><strong>"Content"</strong> means any information, text, images, CVs, job postings, or other materials uploaded to the Platform</li>
            <li><strong>"Services"</strong> means the job listing, job search, application, and recruitment services provided through the Platform</li>
          </ul>

          <h2>3. Eligibility</h2>
          <p>To use our Services, you must:</p>
          <ul>
            <li>Be at least 18 years of age or the legal age of majority in your jurisdiction</li>
            <li>Have the legal capacity to enter into binding agreements</li>
            <li>Not be prohibited from using the Services under South African law or the laws of your jurisdiction</li>
            <li>Provide accurate and truthful information during registration</li>
          </ul>

          <h2>4. User Accounts</h2>
          <h3>4.1 Registration</h3>
          <p>
            To access certain features of the Platform, you must create an account. You agree to provide 
            accurate, current, and complete information during registration and to update such information 
            to keep it accurate.
          </p>
          
          <h3>4.2 Account Security</h3>
          <p>
            You are responsible for maintaining the confidentiality of your account credentials and for all 
            activities that occur under your account. You must notify us immediately of any unauthorised 
            use of your account.
          </p>
          
          <h3>4.3 Account Termination</h3>
          <p>
            We reserve the right to suspend or terminate accounts that violate these Terms, engage in 
            fraudulent activity, or remain inactive for extended periods.
          </p>

          <h2>5. Services Description</h2>
          <h3>5.1 For Job Seekers</h3>
          <ul>
            <li>Create and maintain a professional profile</li>
            <li>Search and apply for job opportunities</li>
            <li>Receive job alerts based on preferences</li>
            <li>Upload CVs and other career documents</li>
          </ul>

          <h3>5.2 For Recruiters</h3>
          <ul>
            <li>Post job advertisements</li>
            <li>Search and filter candidate profiles</li>
            <li>Manage applications and communicate with candidates</li>
            <li>Access recruitment tools and analytics</li>
          </ul>

          <h3>5.3 Subscription Services</h3>
          <p>
            Certain features are available only through paid subscription plans. Details of subscription 
            tiers, pricing, and features are available on our <Link to="/pricing">Pricing Page</Link>.
          </p>

          <h2>6. User Conduct and Prohibited Activities</h2>
          <p>You agree NOT to:</p>
          <ul>
            <li>Post false, misleading, or fraudulent job listings or profile information</li>
            <li>Impersonate any person or entity</li>
            <li>Use the Platform to discriminate against candidates based on race, gender, religion, disability, age, or any other protected characteristic under South African law</li>
            <li>Harvest, collect, or scrape user data without authorisation</li>
            <li>Upload malware, viruses, or harmful code</li>
            <li>Spam users with unsolicited communications</li>
            <li>Use the Platform for any illegal purpose</li>
            <li>Attempt to circumvent security measures</li>
            <li>Post content that is defamatory, obscene, or violates third-party rights</li>
            <li>Engage in activities that violate the Labour Relations Act or Employment Equity Act</li>
          </ul>

          <h2>7. Content and Intellectual Property</h2>
          <h3>7.1 Your Content</h3>
          <p>
            You retain ownership of content you submit to the Platform. By posting content, you grant 
            Job Rocket a non-exclusive, worldwide, royalty-free licence to use, display, and distribute 
            such content for the purpose of providing our Services.
          </p>
          
          <h3>7.2 Our Content</h3>
          <p>
            The Platform, including its design, logos, text, graphics, and software, is owned by Job Rocket 
            and protected by South African and international intellectual property laws. You may not copy, 
            modify, or distribute our content without express written permission.
          </p>

          <h2>8. Fees and Payment</h2>
          <h3>8.1 Pricing</h3>
          <p>
            All prices are displayed in South African Rand (ZAR) and include VAT where applicable, in 
            compliance with the Consumer Protection Act.
          </p>
          
          <h3>8.2 Payment Terms</h3>
          <p>
            Subscription fees are billed in advance on a monthly or annual basis. Payments are processed 
            securely through our payment partners.
          </p>
          
          <h3>8.3 Refunds</h3>
          <p>
            Refund requests are handled in accordance with the Consumer Protection Act. For subscription 
            cancellations, you may continue to use the service until the end of the current billing period.
          </p>

          <h2>9. Employment Law Compliance</h2>
          <p>
            Recruiters using the Platform must comply with all applicable South African employment 
            legislation, including but not limited to:
          </p>
          <ul>
            <li><strong>Employment Equity Act 55 of 1998:</strong> Job advertisements must not unfairly discriminate</li>
            <li><strong>Labour Relations Act 66 of 1995:</strong> Fair labour practices must be observed</li>
            <li><strong>Basic Conditions of Employment Act 75 of 1997:</strong> Working conditions must meet minimum standards</li>
            <li><strong>Skills Development Act 97 of 1998:</strong> Training and development obligations must be met</li>
          </ul>
          <p>
            Job Rocket is not responsible for ensuring compliance by individual recruiters but reserves 
            the right to remove non-compliant job postings.
          </p>

          <h2>10. Disclaimer of Warranties</h2>
          <p>
            To the maximum extent permitted by law, including the Consumer Protection Act:
          </p>
          <ul>
            <li>The Platform is provided "as is" without warranties of any kind</li>
            <li>We do not guarantee that you will find employment or suitable candidates</li>
            <li>We do not verify the accuracy of all user-submitted content</li>
            <li>We do not guarantee uninterrupted or error-free service</li>
          </ul>

          <h2>11. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by South African law, Job Rocket shall not be liable for:
          </p>
          <ul>
            <li>Any indirect, incidental, or consequential damages</li>
            <li>Loss of profits, data, or business opportunities</li>
            <li>Conduct or content of other users</li>
            <li>Employment decisions made based on information on the Platform</li>
          </ul>
          <p>
            Our total liability for any claim shall not exceed the amount you paid us in the 12 months 
            preceding the claim.
          </p>

          <h2>12. Indemnification</h2>
          <p>
            You agree to indemnify and hold harmless Job Rocket, its directors, employees, and agents 
            from any claims, damages, or expenses arising from:
          </p>
          <ul>
            <li>Your use of the Platform</li>
            <li>Your violation of these Terms</li>
            <li>Your violation of any third-party rights</li>
            <li>Content you post on the Platform</li>
          </ul>

          <h2>13. Dispute Resolution</h2>
          <h3>13.1 Governing Law</h3>
          <p>
            These Terms are governed by the laws of the Republic of South Africa. Any disputes shall 
            be subject to the exclusive jurisdiction of the South African courts.
          </p>
          
          <h3>13.2 Alternative Dispute Resolution</h3>
          <p>
            In accordance with the Consumer Protection Act, you may refer consumer complaints to the 
            National Consumer Commission or relevant consumer protection authorities.
          </p>

          <h2>14. Modifications to Terms</h2>
          <p>
            We may modify these Terms at any time. Material changes will be communicated via email or 
            a prominent notice on the Platform at least 30 days before taking effect. Continued use of 
            the Platform after changes constitutes acceptance.
          </p>

          <h2>15. Severability</h2>
          <p>
            If any provision of these Terms is found to be unenforceable, the remaining provisions 
            shall continue in full force and effect.
          </p>

          <h2>16. Entire Agreement</h2>
          <p>
            These Terms, together with our Privacy Policy, constitute the entire agreement between you 
            and Job Rocket regarding the use of the Platform.
          </p>

          <h2>17. Contact Information</h2>
          <p>For questions about these Terms of Service, please contact us:</p>
          <div className="bg-blue-50 p-6 rounded-lg not-prose">
            <p className="font-semibold">Job Rocket (Pty) Ltd</p>
            <p>Johannesburg, Gauteng, South Africa</p>
            <div className="flex items-center space-x-3 mt-3">
              <Mail className="w-5 h-5 text-blue-600" />
              <a href="mailto:legal@jobrocket.co.za" className="text-blue-600 font-semibold">legal@jobrocket.co.za</a>
            </div>
          </div>

          {/* CPA Notice */}
          <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mt-8 not-prose">
            <h3 className="text-lg font-bold text-green-800 mb-2">Consumer Protection Act Notice</h3>
            <p className="text-green-700 text-sm">
              Nothing in these Terms is intended to limit any rights you may have under the Consumer 
              Protection Act 68 of 2008. Where these Terms conflict with your rights under the CPA, 
              the CPA shall prevail.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default TermsOfServicePage;
