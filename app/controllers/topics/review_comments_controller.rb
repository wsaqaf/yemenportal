class Topics::ReviewCommentsController < ApplicationController
  def create
    authorize review_comment, :create?
    if review_comment.save
      redirect_to topic_reviews_path(topic), notice: t(".successfully_created")
    else
      redirect_to topic_reviews_path(topic), alert: t(".not_created")
    end
  end

  def destroy
    authorize review_comment, :destroy?
    if review_comment.destroy
      redirect_to topic_reviews_path(topic), notice: t(".successfully_destroyed")
    else
      redirect_to topic_reviews_path(topic), alert: t(".not_destroyed")
    end
  end

  private

  def review_comment
    @_review_comment ||= if params[:id].present?
      ReviewComment.find(params[:id])
    else
      ReviewComment.new(body: review_comment_params[:body], author: current_user,
        topic: topic)
    end
  end

  def review_comment_params
    params.require(:review_comment).permit(:body)
  end

  def topic
    ::Topic.find(params[:topic_id])
  end
end
