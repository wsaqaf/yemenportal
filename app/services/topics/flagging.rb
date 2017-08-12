class Topics::Flagging
  def initialize(moderator:, topic:, flag:)
    @moderator = moderator
    @topic = topic
    @flag = flag
  end

  def create_review
    if flag.resolve?
      delete_all_other_reviews
      create_review_instance
    else
      delete_review_with_resolve_flag
      create_review_instance
    end
  end

  private

  attr_reader :moderator, :topic, :flag

  def delete_all_other_reviews
    Review.where(topic: topic, moderator: moderator).destroy_all
  end

  def delete_review_with_resolve_flag
    Review.with_resolve_flag(topic, moderator).destroy_all
  end

  def create_review_instance
    Review.create(moderator: moderator, topic: topic, flag: flag)
  end
end
