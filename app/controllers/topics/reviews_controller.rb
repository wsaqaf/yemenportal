class Topics::ReviewsController < ApplicationController
  def index
    render cell: true, model: reviews_page
  end

  def create
  end

  def destroy
  end

  private

  def reviews_page
    Topics::ReviewsPage.new(current_user, topic)
  end

  def topic
    ::Topic.find(params[:topic_id])
  end
end
