class Topics::ReviewsPage
  attr_reader :topic

  def initialize(user, topic)
    @user = user
    @topic = topic
  end

  def flags
    all_flags.map do |flag|
      Flag.new(flag, reviews.select { |review| review.flag == flag })
    end
  end

  private

  attr_reader :user

  def all_flags
    ::Flag.all
      .include_number_of_reviews_for_topic(topic)
  end

  def reviews
    Review.where(moderator: user, topic: topic)
  end

  class Flag
    attr_reader :flag, :review

    def initialize(flag, review)
      @flag = flag
      @review = review
    end

    delegate :id, :name, :color, :number_of_reviews_for_topic, to: :flag

    def reviewed?
      review.present?
    end
  end
end
