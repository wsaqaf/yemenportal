class ApplicationMailer < ActionMailer::Base
  default from: "support@yemenportal.net"
  layout "mailer"

  private

  def support_email
    "support@yemenportal.net"
  end
end
