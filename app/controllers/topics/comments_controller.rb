class Topics::CommentsController < ApplicationController
  def index
    render cell: "topics/comments", model: topic
  end

  private

  def topic
    ::Topic.find(params[:topic_id])
  end
end
