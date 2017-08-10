class Topics::VotesController < ApplicationController
  before_action :authenticate_user!

  def update
    if params[:type] == "upvote"
      vote_updater.upvote
    elsif params[:type] == "downvote"
      vote_updater.downvote
    end
  end

  def destroy
    vote_updater.delete
  end

  private

  def vote_updater
    Topics::VoteUpdater.new(current_user, topic)
  end

  def topic
    Topic.find(params[:topic_id])
  end
end
