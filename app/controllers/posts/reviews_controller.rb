class Posts::ReviewsController < ApplicationController
  before_action :authenticate_user!, except: :index

  def index
    render cell: true, model: reviews_page
  end

  def create
    authorize ::Review
    if flagging.create_review
      redirect_to(post_reviews_path(post), notice: t(".successfully_created"))
    else
      redirect_to(post_reviews_path(post), alert: t(".not_created"))
    end
  end

  def destroy
    authorize review
    if review.destroy
      redirect_to(post_reviews_path(post), notice: t(".successfully_destroyed"))
    end
  end

  private

  def reviews_page
    Posts::ReviewsPage.new(current_user, post)
  end

  def post
    @_post = posts.find(params[:post_id])
  end

  def posts
    @_posts = ::Post.include_review_comments.include_voted_by_user(current_user)
  end

  def flagging
    Posts::Flagging.new(moderator: current_user, post: post, flag: flag)
  end

  def flag
    @_flag = ::Flag.find(params[:flag_id])
  end

  def review
    @_review = ::Review.find(params[:id])
  end
end
