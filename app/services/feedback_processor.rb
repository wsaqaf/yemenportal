class FeedbackProcessor
  def initialize(feedback, user)
    @feedback = feedback
    @user = user || OpenStruct.new(full_name: feedback.name, email: feedback.email)
  end

  def save
    FeedbackMailer.feedback(feedback, user).deliver
  end

  private

  attr_reader :feedback, :user
end
