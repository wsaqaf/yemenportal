class FeedbacksController < ApplicationController
  def new
    render cell: "feedbacks/new", model: new_feedback
  end

  def create
    if feedback_processor.save
      redirect_to new_feedback_path, notice: t(".sent_successfully")
    else
      flash[:alert] = t(".not_sent")
      render cell: "feedbacks/new", model: received_feedback
    end
  end

  private

  def new_feedback
    Feedback.new
  end

  def feedback_processor
    FeedbackProcessor.new(received_feedback, current_user)
  end

  def received_feedback
    Feedback.new(feedback_params)
  end

  def feedback_params
    params.require(:feedback).permit(:name, :email, :reason, :body)
  end
end
