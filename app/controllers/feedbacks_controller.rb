class FeedbacksController < ApplicationController
  def new
    render cell: "feedbacks/new", model: new_feedback
  end

  def create
  end

  private

  def new_feedback
    FeedbackForm.new(OpenStruct.new)
  end
end
