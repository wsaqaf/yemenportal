class FeedbackMailer < ApplicationMailer
  def feedback(feedback, user)
    @feedback = feedback
    @user = user
    mail(to: support_email)
  end
end
