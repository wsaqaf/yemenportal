class Topics::ReviewsController < ApplicationController
  before_action :authenticate_user!, except: :index

  def index
    render cell: true, model: reviews_page
  end

  def create
    authorize Review, :create?
    if flagging.create_review
      redirect_to(topic_reviews_path(topic), notice: t(".successfully_created"))
    else
      redirect_to(topic_reviews_path(topic), alert: t(".not_created"))
    end
  end

  def destroy
    authorize review, :destroy?
    if review.destroy
      redirect_to(topic_reviews_path(topic), notice: t(".successfully_destroyed"))
    end
  end

  private

  def reviews_page
    Topics::ReviewsPage.new(current_user, topic)
  end

  def topic
    ::Topic.find(params[:topic_id])
  end

  def flagging
    Topics::Flagging.new(moderator: current_user, topic: topic, flag: flag)
  end

  def flag
    Flag.find(params[:flag_id])
  end

  def review
    Review.find(params[:id])
  end
end
