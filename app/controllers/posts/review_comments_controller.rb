class Posts::ReviewCommentsController < ApplicationController
  def create
    authorize review_comment
    if review_comment.save
      redirect_to post_reviews_path(post), notice: t(".successfully_created")
    else
      redirect_to post_reviews_path(post), alert: t(".not_created")
    end
  end

  def destroy
    authorize review_comment, :destroy?
    if review_comment.destroy
      redirect_to post_reviews_path(post), notice: t(".successfully_destroyed")
    else
      redirect_to post_reviews_path(post), alert: t(".not_destroyed")
    end
  end

  private

  def review_comment
    @_review_comment ||= load_review_comment
  end

  def load_review_comment
    if params[:id].present?
      ReviewComment.find(params[:id])
    else
      ReviewComment.new(body: review_comment_params[:body], author: current_user, post: post)
    end
  end

  def review_comment_params
    params.require(:review_comment).permit(:body)
  end

  def post
    @_post = ::Post.find(params[:post_id])
  end
end
