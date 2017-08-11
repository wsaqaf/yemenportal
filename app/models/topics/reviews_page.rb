class Topics::ReviewsPage
  attr_reader :topic

  def initialize(user, topic)
    @user = user
    @topic = topic
  end

  def flags
    Flag.all
      .include_number_of_reviews_for_topic(topic)
      .include_topic_reviewed_by_user(topic, user)
  end

  private

  attr_reader :user
end
