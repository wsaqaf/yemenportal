class TopicsController < ApplicationController
  def show
    render cell: :show, model: main_post_of_topic
  end

  private

  def main_post_of_topic
    Topic.find(params[:id]).main_post
  end
end
