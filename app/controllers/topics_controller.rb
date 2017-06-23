class TopicsController < ApplicationController
  before_action :find_topic, only: [:show]

  def show
    render cell: :show, model: @topic, options: { user: current_user, user_votes: user_voted } if @topic.posts.present?
  end

  private

  def find_topic
    @topic = Topic.find(params.fetch(:id))
  end

  def user_voted
    posts_ids = @topic.posts.ids
    current_user ? current_user.votes.votes_posts(posts_ids) : []
  end
end
