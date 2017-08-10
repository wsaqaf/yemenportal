class Topics::VoteUpdater
  def initialize(user, topic)
    @user = user
    @topic = topic
  end

  def upvote
    if vote.present?
      vote.make_upvote
    else
      Vote.create_upvote(user: user, topic: topic)
    end
    update_topic_voting_result
  end

  def downvote
    if vote.present?
      vote.make_downvote
    else
      Vote.create_downvote(user: user, topic: topic)
    end
    update_topic_voting_result
  end

  def delete
    vote.destroy
    update_topic_voting_result
  end

  private

  attr_reader :user, :topic

  def vote
    Vote.find_by(user: user, topic: topic)
  end

  def update_topic_voting_result
    topic.update_voting_result(voting_result_for_topic)
  end

  def voting_result_for_topic
    Vote.voting_result_for(topic)
  end
end
